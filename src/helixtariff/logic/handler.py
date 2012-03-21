from functools import wraps, partial

from helixcore import error_code, mapping
from helixcore.security import Session
from helixcore.security.auth import CoreAuthenticator
from helixcore.server.response import response_ok
from helixcore.actions.handler import (detalize_error, AbstractHandler,
    set_subject_users_ids)
from helixcore.db.filters import (build_index, build_complex_index,
    CurrencyFilter)
from helixcore.db.wrapper import ObjectCreationError, ObjectDeletionError
from helixcore.error import DataIntegrityError, CurrencyNotFound

from helixtariff.conf import settings
from helixtariff.conf.db import transaction
from helixtariff.db.dataobject import (TarifficationObject, Tariff, Rule,
    UserTariff, TariffViewingContext)
from helixtariff.error import (HelixtariffObjectAlreadyExists,
    TarifficationObjectNotFound, TariffNotFound, TariffCycleDetected,
    TariffUsed, RuleAlreadyExsits, RuleNotFound, RuleCheckingError,
    PriceNotFound, RuleProcessingError, UserTariffNotFound,
    TarifficationObjectAlreadyExsits, ParentTariffWithoutCurrency,
    NonParentTariffWithCurrency, UserTariffAlreadyExsits,
    TariffViewingContextNotFound)
from helixtariff.db.filters import (TarifficationObjectFilter, ActionLogFilter,
    TariffFilter, RuleFilter, UserTariffFilter, TariffViewingContextFilter)
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
        resp = auth.check_access(session_id, 'tariff', method.__name__)
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
        else:
            result = resp
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
    @detalize_error(TarifficationObjectAlreadyExsits, ['name'])
    def add_tariffication_object(self, data, session, curs=None):
        name = data['name']
        to_data = {'environment_id': session.environment_id,
            'name': name}
        to = TarifficationObject(**to_data)
        try:
            mapping.insert(curs, to)
        except ObjectCreationError:
            raise TarifficationObjectAlreadyExsits(name)
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
    @detalize_error(ParentTariffWithoutCurrency, ['currency'])
    @detalize_error(NonParentTariffWithCurrency, ['currency'])
    @detalize_error(ObjectCreationError, ['name'])
    @detalize_error(CurrencyNotFound, ['name'])
    def add_tariff(self, data, session, curs=None):
        # checking parent tariff exist
        pt_id = data['parent_tariff_id']
        currency = data.get('currency', None)
        t_data = {'environment_id': session.environment_id,
            'parent_tariff_id': pt_id, 'name': data['name'],
            'type': data['type'], 'status': data['status']}
        if pt_id is not None:
            if currency is not None:
                raise NonParentTariffWithCurrency
            else:
                t_f = TariffFilter(session, {'id': pt_id}, {}, None)
                t_f.filter_one_obj(curs)
        elif currency is None:
            raise ParentTariffWithoutCurrency
        else:
            c_f = CurrencyFilter({'code': currency}, {}, None)
            c = c_f.filter_one_obj(curs)
            t_data['currency_id'] = c.id

        t = Tariff(**t_data)

        mapping.insert(curs, t)
        return response_ok(id=t.id)

    def _tariffs_chain_data(self, tariffs_idx, leaf_tariff, curs_idx):
        '''
        returns list of dicts: [{'id': 1, 'name': 'a',
            'status': 'active', 'currency': 'RUB' or None}]
        '''
        result = [{'id': leaf_tariff.id, 'name': leaf_tariff.name,
            'status': leaf_tariff.status}]
        chain_tariffs_ids = set([leaf_tariff.id])
        while True:
            pt_id = leaf_tariff.parent_tariff_id
            if pt_id:
                parent_tariff = tariffs_idx[leaf_tariff.parent_tariff_id]
                if parent_tariff.currency_id in curs_idx:
                    cur_code = curs_idx[parent_tariff.currency_id].code
                else:
                    cur_code = None

                result.append({'id': parent_tariff.id, 'name': parent_tariff.name,
                    'status': parent_tariff.status, 'currency': cur_code})
                leaf_tariff = parent_tariff

                if pt_id in chain_tariffs_ids:
                    raise TariffCycleDetected('Tariffs chain detected: %s' % result)
                chain_tariffs_ids.add(pt_id)
            else:
                break
        return result

    @transaction()
    @authenticate
    @detalize_error(HelixtariffObjectAlreadyExists, 'new_name')
    @detalize_error(TariffNotFound, 'id')
    @detalize_error(TariffCycleDetected, 'new_parent_name')
    @detalize_error(ParentTariffWithoutCurrency, ['new_parent_tariff_id', 'new_currency'])
    @detalize_error(NonParentTariffWithCurrency, ['new_currency'])
    @detalize_error(CurrencyNotFound, ['new_currency'])
    def modify_tariff(self, data, session, curs=None):
        f = TariffFilter(session, {'id': data.get('id')}, {}, None)
        loader = partial(f.filter_one_obj, curs, for_update=True)

        if 'new_currency' in data:
            curr = data.pop('new_currency')
            if curr is not None:
                c_f = CurrencyFilter({'code': curr}, {}, None)
                c = c_f.filter_one_obj(curs)
                curr_id = c.id
            else:
                curr_id = None
            data['new_currency_id'] = curr_id

        try:
            updated_objs = self.update_obj(curs, data, loader)
            t = updated_objs[0]

            # checking only parent tariff with currency
            if t.parent_tariff_id is None and t.currency_id is None:
                raise ParentTariffWithoutCurrency
            if t.currency_id is not None and t.parent_tariff_id is not None:
                raise NonParentTariffWithCurrency

            # checking tariff cycle
            all_ts_f = TariffFilter(session, {}, {}, None)
            all_ts = all_ts_f.filter_objs(curs)
            all_ts_idx = build_index(all_ts)

            all_curs_idx = self._all_curs_idx(curs)

            self._tariffs_chain_data(all_ts_idx, t, all_curs_idx)

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

    def _collapse_context(self, raw_context):
        res = {}
        for d in raw_context:
            res[d['name']] = d['value']
        return res

    def _expand_context(self, context):
        res = []
        for k, v in context.items():
            res.append({'name': k, 'value': v})
        return res

    @transaction()
    @authenticate
    @detalize_error(TariffNotFound, ['tariff_id'])
    def add_tariff_viewing_context(self, data, session, curs=None):
        # checking parent tariff exist
        t_id = data['tariff_id']
        t_f = TariffFilter(session, {'id': t_id}, {}, None)
        t_f.filter_one_obj(curs)

        raw_ctx = data['context']
        ctx = self._collapse_context(raw_ctx)
        t_v_data = {'environment_id': session.environment_id,
            'tariff_id': t_id, 'name': data['name'],
            'view_order': data['view_order'], 'context': ctx}

        t_v_ctx = TariffViewingContext(**t_v_data)
        mapping.insert(curs, t_v_ctx)
        return response_ok(id=t_v_ctx.id)

    @transaction()
    @authenticate
    def get_tariff_viewing_contexts(self, data, session, curs=None):
        ordering_params = data.get('ordering_params', ['view_order'])
        t_f = TariffViewingContextFilter(session, data['filter_params'],
            data['paging_params'], ordering_params)
        ts, total = t_f.filter_counted(curs)

        def viewer(t_v_ctx):
            res = t_v_ctx.to_dict()
            res = mapping.objects.deserialize_field(res, 'serialized_context', 'context')
            res['context'] = self._expand_context(res['context'])
            res.pop('environment_id')
            return res
        return response_ok(tariff_contexts=self.objects_info(ts, viewer), total=total)

    @transaction()
    @authenticate
    @detalize_error(TariffViewingContextNotFound, 'id')
    @detalize_error(TariffNotFound, 'new_tariff_id')
    def modify_tariff_viewing_context(self, data, session, curs=None):
        f = TariffViewingContextFilter(session, {'id': data.get('id')}, {}, None)
        loader = partial(f.filter_one_obj, curs, for_update=True)

        if 'new_tariff_id' in data:
            t_id = data.get('new_tariff_id')
            t_f = TariffFilter(session, {'id': t_id}, {}, None)
            t_f.filter_one_obj(curs)

        if 'new_context' in data:
            data['new_context'] = self._collapse_context(data['new_context'])
            data = mapping.objects.serialize_field(data, 'new_context',
                'new_serialized_context')

        self.update_obj(curs, data, loader)
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

    def _calculate_rule_info(self, r, r_field_name, t, calculation_ctx):
        raw_rule = getattr(r, r_field_name)
        req = RequestPrice(raw_rule, **calculation_ctx)
        resp = engine.process(req)
        return {
            'rule_id': r.id, 'rule_from_tariff_id': t.id,
            'rule_from_tariff_name': t.name,
            'price': resp.price
        }

    def _find_rule_tariff(self, to, ts_chain_ids, all_ts_idx, rs_to_t_idx, r_field_name,
        calculation_ctx):
        for t_id in ts_chain_ids:
            t = all_ts_idx[t_id]
            # Ignoring inactive tariffs
            if t.status == Tariff.STATUS_INACTIVE:
                continue
            # Processing current rule
            r_to_t_id = '%s_%s' % (to.id, t_id)
            r = rs_to_t_idx.get(r_to_t_id)
            if r:
                raw_rule = getattr(r, r_field_name, None)
                if raw_rule:
                    return r, t
        return None, None

    def _price_info(self, session, curs, data, rule_field_name):

        # Getting required data for price calculation
        to_id = data['tariffication_object_id']
        to_f = TarifficationObjectFilter(session, {'id': to_id}, {}, None)
        to = to_f.filter_one_obj(curs)

        # TODO: handle user tariffs
        all_ts_f = TariffFilter(session, {}, {}, None)
        all_ts = all_ts_f.filter_objs(curs)
        all_ts_idx = build_index(all_ts)

        t_id = data['tariff_id']
        if t_id not in all_ts_idx:
            raise TariffNotFound(tariff_id=t_id)
        if 'user_id' in data:
            ut_f = UserTariffFilter(session, {'user_id': data['user_id'],
                'tariff_id': t_id}, {}, None)
            ut_f.filter_one_obj(curs)

        all_curs_idx = self._all_curs_idx(curs)

        t = all_ts_idx[t_id]
        ts_chain_data = self._tariffs_chain_data(all_ts_idx, t, all_curs_idx)
        ts_chain_ids = [t_data['id'] for t_data in ts_chain_data]

        # Fetching active rules
        r_f = RuleFilter(session, {'tariff_ids': ts_chain_ids,
            'tariffication_object_id': to_id, 'status': Rule.STATUS_ACTIVE}, {}, None)
        rs = r_f.filter_objs(curs)
        rs_to_t_idx = build_complex_index(rs, ('tariffication_object_id', 'tariff_id'))

        # Generation price info
        calculation_ctx = data.get('calculation_context', {})

        r, t = self._find_rule_tariff(to, ts_chain_ids, all_ts_idx, rs_to_t_idx,
            rule_field_name, calculation_ctx)
        if r is None:
            raise PriceNotFound

        price_info = self._calculate_rule_info(r, rule_field_name, t, calculation_ctx)
        price_info['tariffication_object_id'] = to.id
        price_info['tariffication_object_name'] = to.name
        if 'calculation_context' in data:
            price_info['calculation_context'] = calculation_ctx
        return price_info

    @transaction()
    @authenticate
    @detalize_error(TariffNotFound, 'tariff_id')
    @detalize_error(TarifficationObjectNotFound, 'tariffication_object_id')
    @detalize_error(UserTariffNotFound, ['user_id', 'tariff_id'])
    @detalize_error(PriceNotFound, ['tariff_id', 'tariffication_object_id'])
    @detalize_error(RuleProcessingError, ['tariff_id', 'tariffication_object_id'])
    def get_price(self, data, session, curs=None):
        price_info = self._price_info(session, curs, data, 'rule')
        return response_ok(**price_info)

    @transaction()
    @authenticate
    @detalize_error(TariffNotFound, 'tariff_id')
    @detalize_error(TarifficationObjectNotFound, 'tariffication_object_id')
    @detalize_error(UserTariffNotFound, ['user_id', 'tariff_id'])
    @detalize_error(PriceNotFound, ['tariff_id', 'tariffication_object_id'])
    @detalize_error(RuleProcessingError, ['tariff_id', 'tariffication_object_id'])
    def get_draft_price(self, data, session, curs=None):
        price_info = self._price_info(session, curs, data, 'draft_rule')
        return response_ok(**price_info)

    def _all_curs_idx(self, curs):
        all_curs_f = CurrencyFilter({}, {}, None)
        all_curs = all_curs_f.filter_objs(curs)
        return build_index(all_curs)

    def _tariff_price_info(self, session, curs, t, all_tos_idx, all_ts_idx,
        active_rs_to_t_id_idx, calculation_ctxs):

        all_curs_idx = self._all_curs_idx(curs)
        processed_tos = []
        tariff_chain_data = self._tariffs_chain_data(all_ts_idx, t, all_curs_idx)

        ts_chain_ids = [t_data['id'] for t_data in tariff_chain_data]
        tos_ids = set([x.tariffication_object_id for x in active_rs_to_t_id_idx.values()
            if x.tariff_id in ts_chain_ids])

        for to_id in tos_ids:
            to = all_tos_idx[to_id]
            prices = []
            view_order = 0
            for calculation_ctx in calculation_ctxs:
                price_info = {}
                for r_field_name in ('rule', 'draft_rule'):
                    cur_r, cur_t = self._find_rule_tariff(to, ts_chain_ids, all_ts_idx,
                        active_rs_to_t_id_idx, r_field_name, calculation_ctx)
                    if cur_r is not None and getattr(cur_r, r_field_name) is not None:
                        price_info[r_field_name] = self._calculate_rule_info(cur_r,
                            r_field_name, cur_t, calculation_ctx)
                        view_order = max(view_order, cur_r.view_order)
                # actual or draft price found
                if len(price_info):
                    price_info['calculation_context'] = calculation_ctx
                    prices.append(price_info)
            if len(price_info):
                to_info = {'tariffication_object_id': to.id,
                    'tariffication_object_name': to.name,
                    'view_order': view_order,
                    'prices': prices}
                processed_tos.append(to_info)

        processed_tos.sort(key=lambda tos_data: tos_data['view_order'])
        t_p_info = {'tariff_id': t.id, 'tariff_name': t.name,
            'tariff_status': t.status, 'tariffication_objects': processed_tos}

        return t_p_info

    @transaction()
    @authenticate
    def get_tariffs_prices(self, data, session, curs=None):
        f_params = data['filter_params']
        if 'user_id' in f_params:
            user_id = f_params['user_id']
            ts_ids = f_params['ids']
            ut_f = UserTariffFilter(session, {'user_id': user_id,
                'tariff_ids': ts_ids}, {}, None)
            uts = ut_f.filter_objs(curs)
            uts_tariff_ids = [ut.tariff_id for ut in uts]
            ts_ids = filter(lambda x: x in uts_tariff_ids, ts_ids)
            f_params['ids'] = ts_ids


        t_f = TariffFilter(session, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        ts, total = t_f.filter_counted(curs)
        ts_idx = build_index(ts)
        ts_ids = filter(lambda x: x in ts_idx, data['filter_params']['ids'])

        all_tos_f = TarifficationObjectFilter(session, {}, {}, None)
        all_tos = all_tos_f.filter_objs(curs)
        all_tos_idx = build_index(all_tos)

        all_ts_f = TariffFilter(session, {}, {}, None)
        all_ts = all_ts_f.filter_objs(curs)
        all_ts_idx = build_index(all_ts)

        active_r_f = RuleFilter(session, {}, {}, None)
        active_rs = active_r_f.filter_objs(curs)
        active_rs_to_t_idx = build_complex_index(active_rs,
            ('tariffication_object_id', 'tariff_id'))

        tariffs_prices = []
        calculation_ctxs = data['calculation_contexts']
        for t_id in ts_ids:
            tariff_price_info = self._tariff_price_info(session, curs, ts_idx[t_id],
                all_tos_idx, all_ts_idx, active_rs_to_t_idx, calculation_ctxs)
            tariffs_prices.append(tariff_price_info)

        return response_ok(tariffs=tariffs_prices, total=total)

    @set_subject_users_ids('user_id')
    @transaction()
    @authenticate
    @detalize_error(TariffNotFound, ['tariff_id'])
    @detalize_error(UserTariffAlreadyExsits, ['tariff_id', 'user_id'])
    def add_user_tariff(self, data, session, curs=None):
        # checking tariff exist
        t_id = data['tariff_id']
        u_id = data['user_id']
        if t_id:
            t_f = TariffFilter(session, {'id': t_id}, {}, None)
            t_f.filter_one_obj(curs)

        ut_data = {'environment_id': session.environment_id,
            'tariff_id': t_id, 'user_id': u_id}
        ut = UserTariff(**ut_data)
        try:
            mapping.insert(curs, ut)
        except ObjectCreationError:
            raise UserTariffAlreadyExsits(tariff_id=t_id, user_id=u_id)
        return response_ok(id=ut.id)

    @set_subject_users_ids('user_id')
    @transaction()
    @authenticate
    def delete_user_tariffs(self, data, session, curs=None):
        f = UserTariffFilter(session, {'user_id': data['user_id'],
            'tariff_ids': data['tariff_ids']}, {}, ['id'])
        mapping.delete_objects(curs, f.filter_objs(curs, for_update=True))
        return response_ok()

    @transaction()
    @authenticate
    def get_user_tariffs(self, data, session, curs=None):
        ut_f = UserTariffFilter(session, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        uts = ut_f.filter_objs(curs)

        uts_data = {}
        for ut in uts:
            if ut.user_id not in uts_data:
                uts_data[ut.user_id] = []
            uts_data[ut.user_id].append(ut.tariff_id)
        uts_info = [{'user_id': k, 'tariff_ids': v} for k, v in uts_data.items()]
        uts_info.sort(key=lambda x: x['user_id'])
        return response_ok(user_tariffs=uts_info, total=len(uts_info))
