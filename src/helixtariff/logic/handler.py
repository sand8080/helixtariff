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
    TariffUsed, RuleAlreadyExsits, RuleNotFound)
from helixcore.error import DataIntegrityError
from helixtariff.db.filters import (TarifficationObjectFilter, ActionLogFilter,
    TariffFilter, RuleFilter)
from helixcore.db.filters import build_index



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
    @detalize_error(RuleAlreadyExsits, 'rules')
    @detalize_error(RuleNotFound, 'rules')
    @detalize_error(TariffNotFound, 'rules')
    @detalize_error(TarifficationObjectNotFound, 'rules')
    def save_rules(self, data, session, curs=None):
        rules = data['rules']
        ids = []
        if not rules:
            return response_ok(ids=ids)

        all_t_f = TariffFilter(session, {}, {}, None)
        all_ts = all_t_f.filter_objs(curs)
        all_ts_idx = build_index(all_ts)

        all_to_f = TarifficationObjectFilter(session, {}, {}, None)
        all_tos = all_to_f.filter_objs(curs)
        all_tos_idx = build_index(all_tos)

        all_r_f = RuleFilter(session, {}, {}, None)
        all_rs = all_r_f.filter_objs(curs)
        all_rs_idx = build_index(all_rs)

        for rule_data in rules:
            r = Rule(environment_id=session.environment_id, **rule_data)
            rule_id = rule_data.get('id')
            if rule_id not in all_rs_idx:
                raise RuleNotFound(id=rule_id)
            if r.tariff_id not in all_ts_idx:
                raise TariffNotFound(rule_id=rule_id, tariff_id=r.tariff_id)
            if r.tariffication_object_id not in all_tos_idx:
                raise TarifficationObjectNotFound(rule_id=rule_id,
                    tariffication_object_id=r.tariffication_object_id)
            # TODO: add draft rule checking
            try:
                mapping.save(curs, r)
            except ObjectCreationError:
                raise RuleAlreadyExsits(r)
            ids.append(r.id)
        return response_ok(ids=ids)
