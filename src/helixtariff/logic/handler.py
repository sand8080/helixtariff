from functools import wraps, partial

from helixcore import error_code, mapping
from helixcore.security import Session
from helixcore.security.auth import CoreAuthenticator
from helixcore.server.response import response_ok


from helixtariff.conf import settings
from helixtariff.conf.db import transaction
from helixcore.actions.handler import detalize_error, AbstractHandler
from helixcore.db.wrapper import ObjectCreationError, ObjectDeletionError
from helixtariff.db.dataobject import TarifficationObject, Tariff, Rule
from helixtariff.error import (HelixtariffObjectAlreadyExists,
    TarifficationObjectNotFound, TariffNotFound, TariffCycleDetected,
    TariffUsed, RuleAlreadyExsits, RuleNotFound, RuleCheckingError,
    PriceNotFound, RuleProcessingError)
from helixcore.error import DataIntegrityError
from helixtariff.db.filters import (TarifficationObjectFilter, ActionLogFilter,
    TariffFilter, RuleFilter)
from helixcore.db.filters import build_index
from helixtariff.rulesengine.checker import RuleChecker
from helixtariff.rulesengine import engine
from helixtariff.rulesengine.engine import RequestPrice



def _add_log_info(data, session, custom_actor_info=None):
    data['actor_user_id'] = session.user_id
    data['environment_id'] = session.environment_id
    data['session_id'] = session.session_id
    if custom_actor_info:
        data['custom_actor_info'] = custom_actor_info


def authenticate(method):
    @wraps(method)
    def decroated(self, data, curs):
        auth = CoreAuthenticator(settings.auth_server_url)
        session_id = data['session_id']
        custom_actor_info = data.pop('custom_actor_info', None)
        resp = auth.check_access(session_id, 'billing', method.__name__)
        if resp.get('status') == 'ok':
            session = Session(session_id, '%s' % resp['environment_id'],
                '%s' % resp['user_id'])
            if resp.get('access') == 'granted':
                try:
                    result = method(self, data, session, curs=curs)
                except Exception, e:
                    data['environment_id'] = session.environment_id
                    _add_log_info(data, session, custom_actor_info)
                    raise e
            else:
                result = {'status': 'error', 'code': error_code.HELIX_AUTH_ERROR,
                    'message': 'Access denied'}
            _add_log_info(data, session, custom_actor_info)
        return result
    return decroated


class Handler(AbstractHandler):
    '''
    Handles all API actions. Method names are called like actions.
    '''

    def ping(self, _):
        return response_ok()

    def login(self, data):
        auth = CoreAuthenticator(settings.auth_server_url)
        resp = auth.login(data)
        return resp

    def logout(self, data):
        auth = CoreAuthenticator(settings.auth_server_url)
        resp = auth.logout(data)
        return resp

    @transaction()
    @authenticate
    @detalize_error(ObjectCreationError, ['name'])
    def add_tariffication_object(self, data, session, curs=None):
        to_data = {'environment_id': session.environment_id,
            'name': data['name']}
        to = TarifficationObject(**to_data)
        mapping.insert(curs, to)
        return response_ok(id=to.id)

    @transaction()
    @authenticate
    def get_tariffication_objects(self, data, session, curs=None):
        to_f = TarifficationObjectFilter(session, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        tos, total = to_f.filter_counted(curs)
        def viewer(to):
            return {
                'id': to.id,
                'name': to.name,
            }
        return response_ok(tariffication_objects=self.objects_info(tos, viewer), total=total)

    @transaction()
    @authenticate
    @detalize_error(HelixtariffObjectAlreadyExists, 'new_name')
    @detalize_error(TarifficationObjectNotFound, 'id')
    def modify_tariffication_object(self, data, session, curs=None):
        f = TarifficationObjectFilter(session, {'id': data.get('id')}, {}, None)
        loader = partial(f.filter_one_obj, curs, for_update=True)
        try:
            self.update_obj(curs, data, loader)
        except DataIntegrityError:
            raise HelixtariffObjectAlreadyExists('Tariffication object %s already exists' %
                data.get('new_name'))
        return response_ok()

    @transaction()
    @authenticate
    @detalize_error(TarifficationObjectNotFound, 'id')
    def delete_tariffication_object(self, data, session, curs=None):
        f = TarifficationObjectFilter(session, {'id': data.get('id')}, {}, None)
        mapping.delete(curs, f.filter_one_obj(curs))
        return response_ok()

    @transaction()
    @authenticate
    def get_action_logs(self, data, session, curs=None):
        return self._get_action_logs(data, session, curs)

    @transaction()
    @authenticate
    def get_action_logs_self(self, data, session, curs=None):
        data['filter_params']['user_id'] = session.user_id
        return self._get_action_logs(data, session, curs)

    def _get_action_logs(self, data, session, curs):
        f_params = data['filter_params']
        u_id = f_params.pop('user_id', None)
        if u_id:
            f_params[('subject_users_ids', 'actor_user_id')] = (u_id, u_id)
        f = ActionLogFilter(session.environment_id, f_params,
            data['paging_params'], data.get('ordering_params'))
        action_logs, total = f.filter_counted(curs)
        def viewer(obj):
            result = obj.to_dict()
            result.pop('environment_id', None)
            result['request_date'] = '%s' % result['request_date']
            return result
        return response_ok(action_logs=self.objects_info(action_logs, viewer),
            total=total)

    @transaction()
    @authenticate
    @detalize_error(TariffNotFound, ['parent_tariff_id'])
    @detalize_error(ObjectCreationError, ['name'])
    def add_tariff(self, data, session, curs=None):
        # checking parent tariff exist
        pt_id = data['parent_tariff_id']
        if pt_id:
            t_f = TariffFilter(session, {'id': pt_id}, {}, None)
            t_f.filter_one_obj(curs)

        t_data = {'environment_id': session.environment_id,
            'parent_tariff_id': pt_id, 'name': data['name'],
            'type': data['type'], 'status': data['status']}
        t = Tariff(**t_data)

        mapping.insert(curs, t)
        return response_ok(id=t.id)

    def _tariffs_chain_data(self, tariffs_idx, leaf_tariff):
        '''
        returns list of dicts: [{'id': 1, 'name': 'a',
            'status': 'active'}]
        '''
        result = [{'id': leaf_tariff.id, 'name': leaf_tariff.name,
            'status': leaf_tariff.status}]
        chain_tariffs_ids = set([leaf_tariff.id])
        while True:
            pt_id = leaf_tariff.parent_tariff_id
            if pt_id:
                parent_tariff = tariffs_idx[leaf_tariff.parent_tariff_id]
                result.append({'id': parent_tariff.id, 'name': parent_tariff.name,
                    'status': parent_tariff.status})
                leaf_tariff = parent_tariff

                if pt_id in chain_tariffs_ids:
                    raise TariffCycleDetected('Tariffs chain detected: %s' % result)
                chain_tariffs_ids.add(pt_id)
            else:
                break
        return result

    @transaction()
    @authenticate
    def get_tariffs(self, data, session, curs=None):
        t_f = TariffFilter(session, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        ts, total = t_f.filter_counted(curs)

        all_ts_f = TariffFilter(session, {}, {}, None)
        all_ts = all_ts_f.filter_objs(curs)
        all_ts_idx = build_index(all_ts)

        def viewer(t):
            ts_chain_data = self._tariffs_chain_data(all_ts_idx, t)
            return {'id': t.id, 'name': t.name, 'type': t.type,
                'status': t.status, 'parent_tariffs': ts_chain_data[1:]}
        return response_ok(tariffs=self.objects_info(ts, viewer), total=total)

    @transaction()
    @authenticate
    @detalize_error(HelixtariffObjectAlreadyExists, 'new_name')
    @detalize_error(TarifficationObjectNotFound, 'id')
    @detalize_error(TariffCycleDetected, 'new_parent_name')
    def modify_tariff(self, data, session, curs=None):
        f = TariffFilter(session, {'id': data.get('id')}, {}, None)
        loader = partial(f.filter_one_obj, curs, for_update=True)

        try:
            updated_objs = self.update_obj(curs, data, loader)
            t = updated_objs[0]

            # checking tariff cycle
            all_ts_f = TariffFilter(session, {}, {}, None)
            all_ts = all_ts_f.filter_objs(curs)
            all_ts_idx = build_index(all_ts)

            self._tariffs_chain_data(all_ts_idx, t)

        except DataIntegrityError:
            raise HelixtariffObjectAlreadyExists('Tariff %s already exists' %
                data.get('new_name'))
        return response_ok()

    @transaction()
    @authenticate
    @detalize_error(TariffNotFound, 'id')
    @detalize_error(TariffUsed, 'id')
    def delete_tariff(self, data, session, curs=None):
        f = TariffFilter(session, {'id': data['id']}, {}, None)
        try:
            mapping.delete(curs, f.filter_one_obj(curs))
        except ObjectDeletionError:
            raise TariffUsed('Tariff %s used' % data['id'])
        return response_ok()

    @transaction()
    @authenticate
    @detalize_error(RuleAlreadyExsits, ['tariff_id', 'tariffication_object_id'])
    @detalize_error(RuleNotFound, 'id')
    @detalize_error(TariffNotFound, 'tariff_id')
    @detalize_error(TarifficationObjectNotFound, 'tariffication_object_id')
    @detalize_error(RuleCheckingError, 'draft_rule')
    def save_rule(self, data, session, curs=None):
        all_t_f = TariffFilter(session, {}, {}, None)
        all_ts = all_t_f.filter_objs(curs)
        all_ts_idx = build_index(all_ts)

        all_to_f = TarifficationObjectFilter(session, {}, {}, None)
        all_tos = all_to_f.filter_objs(curs)
        all_tos_idx = build_index(all_tos)

        all_r_f = RuleFilter(session, {}, {}, None)
        all_rs = all_r_f.filter_objs(curs)
        all_rs_idx = build_index(all_rs)

        r_data = {'environment_id': session.environment_id,
            'tariff_id': data['tariff_id'], 'status': data['status'],
            'tariffication_object_id': data['tariffication_object_id'],
            'draft_rule': data['draft_rule']}
        r_data['view_order'] = data.get('view_order', 0)
        rule_id = data.get('id')
        if rule_id:
            r_data['id'] = rule_id
        r = Rule(**r_data)

        if rule_id and rule_id not in all_rs_idx:
            raise RuleNotFound(id=rule_id)
        if r.tariff_id not in all_ts_idx:
            raise TariffNotFound(rule_id=rule_id, tariff_id=r.tariff_id)
        if r.tariffication_object_id not in all_tos_idx:
            raise TarifficationObjectNotFound(rule_id=rule_id,
                tariffication_object_id=r.tariffication_object_id)
        checker = RuleChecker()
        checker.check(r.draft_rule)

        try:
            mapping.save(curs, r)
        except ObjectCreationError:
            raise RuleAlreadyExsits(r)
        return response_ok(id=r.id)

    @transaction()
    @authenticate
    def get_rules(self, data, session, curs=None):
        r_f = RuleFilter(session, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        rs, total = r_f.filter_counted(curs)
        if total:
            all_to_f = TarifficationObjectFilter(session, {}, {}, None)
            all_tos = all_to_f.filter_objs(curs)
            all_tos_idx = build_index(all_tos)

            all_ts_f = TariffFilter(session, {}, {}, None)
            all_ts = all_ts_f.filter_objs(curs)
            all_ts_idx = build_index(all_ts)
        else:
            all_tos_idx = {}
            all_ts_idx = {}

        def viewer(r):
            t = all_ts_idx[r.tariff_id]
            to = all_tos_idx[r.tariffication_object_id]
            return {'id': r.id, 'tariff_id': t.id, 'tariff_name': t.name,
                'tariffication_object_id': to.id, 'tariffication_object_name': to.name,
                'status': r.status, 'rule': r.rule, 'draft_rule': r.draft_rule,
                'view_order': r.view_order}
        return response_ok(rules=self.objects_info(rs, viewer), total=total)

    @transaction()
    @authenticate
    @detalize_error(RuleNotFound, 'id')
    def delete_rule(self, data, session, curs=None):
        f = RuleFilter(session, {'id': data['id']}, {}, None)
        mapping.delete(curs, f.filter_one_obj(curs))
        return response_ok()

    @transaction()
    @authenticate
    @detalize_error(TariffNotFound, 'tariff_id')
    @detalize_error(RuleCheckingError, 'tariff_id')
    def apply_draft_rules(self, data, session, curs=None):
        t_f = TariffFilter(session, {'id': data['tariff_id']}, {}, None)
        t_f.filter_one_obj(curs)

        f = RuleFilter(session, {'tariff_id': data['tariff_id']}, {}, ['id'])
        rs = f.filter_objs(curs, for_update=True)
        checker = RuleChecker()
        for r in rs:
            if r.draft_rule:
                checker.check(r.draft_rule)
                r.rule = r.draft_rule
                r.draft_rule = None
                mapping.update(curs, r)
        return response_ok()

#    Useful for price plan calculation
#    def _tariffications_objects_chain_data(self, ts_idx, tos_idx, ts_chain_data):
#        result = []
#        processed_tos_ids = set()
#        for t_data in ts_chain_data:
#            t_id = t_data['id']
#            t = ts_idx[t_id]
#            tos_to_process = t.tariffication_objects_ids
#            for to_id in tos_to_process:
#                if to_id not in processed_tos_ids:
#                    to = tos_idx[to_id]
#                    to_data = {'id': to.id, 'name': to.name,
#                        'tariff_id': t.id}
#                    result.append(to_data)
#                    processed_tos_ids.add(to_id)
#        return result
#
#    def _filter_exist_tariffication_objects_ids(self, curs, session, tos_ids):
#        to_f = TarifficationObjectFilter(session, {}, {}, None)
#        tos = to_f.filter_objs(curs)
#        exist_tos_idx = build_index(tos)
#        exist_tos_ids = exist_tos_idx.keys()
#        return filter(lambda x: x in exist_tos_ids, tos_ids)

    def _calculate_rule_info(self, rule, tariff, calculation_ctx):
        req = RequestPrice(rule.rule, **calculation_ctx)
        resp = engine.process(req)
        return {
            'id': rule.id, 'rule_from_tariff_id': tariff.id,
            'rule_from_tariff_name': tariff.name,
            'price': resp.price
        }

    def _price_info(self, session, curs, data, rule_field_name):
        if 'user_id' in data:
            # TODO: handle after user tariffs implementation
            raise NotImplementedError('user_id not handled in get_price yet')
        t_id = data['tariff_id']
        to_id = data['tariffication_object_id']

        # Getting required data for price calculation
        to_f = TarifficationObjectFilter(session, {'id': to_id}, {}, None)
        to = to_f.filter_one_obj(curs)

        # TODO: handle user tariffs
        ts_f = TariffFilter(session, {}, {}, None)
        ts = ts_f.filter_objs(curs)
        ts_idx = build_index(ts)

        if t_id not in ts_idx:
            raise TariffNotFound(tariff_id=t_id)

        t = ts_idx[t_id]
        ts_chain_data = self._tariffs_chain_data(ts_idx, t)
        ts_ids = [t_data['id'] for t_data in ts_chain_data]

        # Fetching active rules
        r_f = RuleFilter(session, {'tariff_ids': ts_ids,
            'tariffication_object_id': to_id, 'status': Rule.STATUS_ACTIVE}, {}, None)
        rs = r_f.filter_objs(curs)
        rs_tariff_id_idx = build_index(rs, 'tariff_id')

        # Generation price info
        calculation_ctx = data.get('calculation_context', {})
        price_info = {}

        for cur_t_id in ts_ids:
            cur_t = ts_idx[cur_t_id]
            # Ignoring inactive tariffs
            if cur_t.status == Tariff.STATUS_INACTIVE:
                continue
            # Processing current rule
            cur_r = rs_tariff_id_idx.get(cur_t_id)
            if cur_r:
                raw_rule = getattr(cur_r, rule_field_name, None)
                if raw_rule:
                    resp = engine.process(RequestPrice(raw_rule, **calculation_ctx))
                    price_info = {
                        'price': resp.price,
                        'rule_id': cur_r.id,
                        'tariffication_object_id': to.id,
                        'tariffication_object_name': to.name,
                        'rule_from_tariff_id': cur_t.id,
                        'rule_from_tariff_name': cur_t.name,
                    }
                    if 'calculation_context' in data:
                        price_info['calculation_context'] = calculation_ctx
                    break
        if not price_info:
            raise PriceNotFound
        return price_info

    @transaction()
    @authenticate
    @detalize_error(TariffNotFound, 'tariff_id')
    @detalize_error(TarifficationObjectNotFound, 'tariffication_object_id')
    @detalize_error(PriceNotFound, ['tariff_id', 'tariffication_object_id'])
    @detalize_error(RuleProcessingError, ['tariff_id', 'tariffication_object_id'])
    def get_price(self, data, session, curs=None):
        price_info = self._price_info(session, curs, data, 'rule')
        return response_ok(**price_info)

    @transaction()
    @authenticate
    @detalize_error(TariffNotFound, 'tariff_id')
    @detalize_error(TarifficationObjectNotFound, 'tariffication_object_id')
    @detalize_error(PriceNotFound, ['tariff_id', 'tariffication_object_id'])
    @detalize_error(RuleProcessingError, ['tariff_id', 'tariffication_object_id'])
    def get_draft_price(self, data, session, curs=None):
        price_info = self._price_info(session, curs, data, 'draft_rule')
        return response_ok(**price_info)

    @transaction()
    @authenticate
    def get_tariffs_prices(self, data, session, curs=None):
        f_params = data['filter_params']
        ts_ids = f_params.get('tariff_ids', [])
#        ts_f_params = {'ids': ts_ids}
        if 'user_ids' in f_params:
            raise NotImplementedError('user_ids filter parameter not handled in get_tariffs_prices yet')

        all_ts_f = TariffFilter(session, {}, {}, None)
        all_ts = all_ts_f.filter_objs(curs)
        all_ts_idx = build_index(all_ts)

        # building all tariffs chains
        ts_chains_data = {}
        for t_id in ts_ids:
            t = all_ts_idx[t_id]
            tariff_chain_data = self._tariffs_chain_data(all_ts_idx, t)
            ts_chains_data[t_id] = tariff_chain_data

        # collecting all tariff ids used in chains
        used_ts_ids = set()
        for _, chains_data in ts_chains_data.items():
            for chain_data in chains_data:
                used_ts_ids.add(chain_data['id'])

#        # selecting active rules
#        r_f_params = {'tariff_ids': list(used_ts_ids)}
#        r_o_params = data.get('ordering_params')
#        r_f = RuleFilter(session, r_f_params, {}, r_o_params)
#        rs = r_f.filter_objs(curs)
#        rs_idx = build_index(rs)
#
#        print '### selected rules', rs_idx
#        rs_ids_by_tariff_id = {}

#        for r in rs:
#            t_id = r.tariff
#            rs_ids_by_tariff_id

#        tos_ids = [r.tariffication_object_id for r in rs]
#        tos_f = TarifficationObjectFilter(session, {'ids': tos_ids}, {}, None)
#        tos = tos_f.filter_objs(curs)
#        tos_idx = build_index(tos)
#
#        calculation_ctxs = data['calculation_contexts']
#
#        result = []
#        for t_id in ts_ids:
#            t_data = {}
#            t = ts_idx[t_id]
#            t_data['tariff_id'] = t.id
#            t_data['tariff_name'] = t.name
#            t_data['tariff_status'] = t.status

        return response_ok(tariffs=[], total=0)