from functools import wraps, partial

from helixcore import error_code, mapping
from helixcore.security import Session
from helixcore.security.auth import CoreAuthenticator
from helixcore.server.response import response_ok


from helixtariff.conf import settings
from helixtariff.conf.db import transaction
from helixcore.actions.handler import detalize_error, AbstractHandler
from helixcore.db.wrapper import ObjectCreationError
from helixtariff.db.dataobject import TarifficationObject, Tariff
from helixtariff.error import (HelixtariffObjectAlreadyExists,
    TarifficationObjectNotFound, TariffNotFound)
from helixcore.error import DataIntegrityError
from helixtariff.db.filters import (TarifficationObjectFilter, ActionLogFilter,
    TariffFilter)
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
        # TODO: remove from tariffs, rules?
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

#    @transaction()
#    @authenticate
#    def add_tariff(self, data, session, curs=None):
#        service_set = selector.get_service_set_by_name(curs, operator, data['service_set'])
#        del data['service_set']
#        data['service_set_id'] = service_set.id
#        parent_tariff = data['parent_tariff']
#        if parent_tariff is None:
#            parent_id = None
#        else:
#            parent_id = selector.get_tariff(curs, operator, parent_tariff).id
#        del data['parent_tariff']
#        data['parent_id'] = parent_id
#        mapping.insert(curs, Tariff(**data))
#        return response_ok()


    def _filter_exist_tariffication_objects_ids(self, curs, session, tos_ids):
        to_f = TarifficationObjectFilter(session, {}, {}, None)
        tos = to_f.filter_objs(curs)
        exist_tos_idx = build_index(tos)
        exist_tos_ids = exist_tos_idx.keys()
        return filter(lambda x: x in exist_tos_ids, tos_ids)

#    def _get_tariffication_objects_tariffs_data(self, leaf_tariff, tariffs_chain_data):
#        result = []
#        tariffs_idx = build_index(tariffs)
#        while True:
#            pt_id = leaf_tariff.parent_tariff_id
#            if pt_id:
#                parent_tariff = tariffs_idx[leaf_tariff.parent_tariff_id]
#                result.append({'id': parent_tariff.id, 'name': parent_tariff.name,
#                    'status': parent_tariff.status})
#                leaf_tariff = parent_tariff
#            else:
#                break
#        return result

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
        while True:
            pt_id = leaf_tariff.parent_tariff_id
            if pt_id:
                parent_tariff = tariffs_idx[leaf_tariff.parent_tariff_id]
                result.append({'id': parent_tariff.id, 'name': parent_tariff.name,
                    'status': parent_tariff.status})
                leaf_tariff = parent_tariff
            else:
                break
        return result

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

    @transaction()
    @authenticate
    def get_tariffs(self, data, session, curs=None):
        t_f = TariffFilter(session, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        ts, total = t_f.filter_counted(curs)

        all_ts_f = TariffFilter(session, {}, {}, None)
        all_ts = all_ts_f.filter_objs(curs)
        all_ts_idx = build_index(all_ts)

#        all_to_f = TarifficationObjectFilter(session, {}, {}, None)
#        all_tos = all_to_f.filter_objs(curs)
#        all_tos_idx = build_index(all_tos)

        def viewer(t):
            ts_chain_data = self._tariffs_chain_data(all_ts_idx, t)
#            to_data = self._tariffications_objects_chain_data(all_ts_idx,
#                all_tos_idx, ts_chain_data)
            return {'id': t.id, 'name': t.name, 'type': t.type,
                'status': t.status, 'parent_tariffs': ts_chain_data[1:]}
        return response_ok(tariffs=self.objects_info(ts, viewer), total=total)

#
#    def _get_new_parent_id(self, curs, operator, tariff_name, new_parent_name):
#        if new_parent_name is None:
#            return None
#        tariffs_names_idx = selector.get_tariffs_names_indexed_by_id(curs, operator)
#        tariffs_ids_idx = dict([(v, k) for (k, v) in tariffs_names_idx.iteritems()])
#
#        if tariff_name not in tariffs_ids_idx:
#            raise TariffNotFound(tariff_name)
#        tariff_id = tariffs_ids_idx[tariff_name]
#
#        if new_parent_name not in tariffs_ids_idx:
#            raise TariffNotFound(new_parent_name)
#        new_parent_id = tariffs_ids_idx[new_parent_name]
#
#        parents_ids_idx = selector.get_tariffs_parent_ids_indexed_by_id(curs, operator)
#        parents_ids_idx[tariff_id] = new_parent_id
#        self._calculate_tariffs_chain(
#            tariff_id,
#            tariffs_names_idx,
#            parents_ids_idx
#        )
#        return new_parent_id
#
#    @transaction()
#    @authentificate
#    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_integrity, 'name')
#    @detalize_error(TariffCycleError, RequestProcessingError.Category.data_integrity, 'parent_tariff')
#    @detalize_error(ServiceSetNotFound, RequestProcessingError.Category.data_integrity, 'service_set')
#    def modify_tariff(self, data, operator, curs=None):
#        t_name = data['name']
#        t = selector.get_tariff(curs, operator, t_name, for_update=True)
#        if 'new_parent_tariff' in data:
#            new_p_name = data['new_parent_tariff']
#            try:
#                data['new_parent_id'] = self._get_new_parent_id(curs, operator, t_name, new_p_name)
#            except TariffNotFound, e:
#                raise RequestProcessingError(RequestProcessingError.Category.data_integrity,
#                    e.message, details={'parent_tariff': e.message})
#            del data['new_parent_tariff']
#        if 'new_service_set' in data:
#            new_ss = selector.get_service_set_by_name(curs, operator, data['new_service_set'])
#            st_names_idx = selector.get_service_types_names_indexed_by_id(curs, operator)
#            old_st_ids = selector.get_service_types_ids(curs, [t.service_set_id])
#            new_st_ids = selector.get_service_types_ids(curs, [new_ss.id])
#            st_names_to_check = [st_names_idx[idx] for idx in set(old_st_ids) - set(new_st_ids)]
#            self._check_types_not_used(curs, operator, [new_ss.id], st_names_to_check)
#            data['new_service_set_id'] = new_ss.id
#            del data['new_service_set']
#        def loader():
#            return t
#        self.update_obj(curs, data, loader)
#        return response_ok()
#
#
#    @transaction()
#    @authentificate
#    @detalize_error(TariffUsed, RequestProcessingError.Category.data_integrity, 'name')
#    def delete_tariff(self, data, operator, curs=None):
#        t_name = data['name']
#        t = selector.get_tariff(curs, operator, t_name, for_update=True)
#        childs = selector.get_child_tariffs(curs, t)
#        if childs:
#            ch_names = [ch.name for ch in childs]
#            raise TariffUsed("Tariff '%s' is parent of %s" % (t.name, ', '.join(ch_names)))
#        rules = selector.get_rules(curs, t, [Rule.TYPE_ACTUAL, Rule.TYPE_DRAFT])
#        undel_rules = filter(lambda x: x.type == Rule.TYPE_ACTUAL and x.enabled, rules)
#        if undel_rules:
#            st_names_idx = selector.get_service_sets_names_indexed_by_id(curs, operator)
#            st_names = [st_names_idx[r.service_type_id] for r in undel_rules]
#            raise TariffUsed("In tariff '%s' defined undeletable rules for services %s" %
#                (t.name, ', '.join(st_names)))
#        else:
#            mapping.delete_objects(curs, rules)
#        mapping.delete(curs, t)
#        return response_ok()
#
#    def _get_tariffs_data(self, curs, operator, tariffs):
#        ss_names = selector.get_service_sets_names_indexed_by_id(curs, operator)
#        t_names_idx = selector.get_tariffs_names_indexed_by_id(curs, operator)
#        pt_ids_idx = selector.get_tariffs_parent_ids_indexed_by_id(curs, operator)
#
#        result = []
#        for tariff in tariffs:
#            t_chain = self._calculate_tariffs_chain(tariff.id, t_names_idx, pt_ids_idx)
#            _, t_names = map(list, zip(*t_chain))
#            try:
#                pt_name = t_names[1]
#            except IndexError:
#                pt_name = None
#
#            result.append(
#                {
#                    'name': tariff.name,
#                    'service_set': ss_names.get(tariff.service_set_id),
#                    'tariffs_chain': t_names,
#                    'parent_tariff': pt_name,
#                    'in_archive': tariff.in_archive,
#                }
#            )
#        return result
#
#    def _tariffs_chain_names(self, tariff_id, tariffs_ids, tariffs_names):
#        return tariffs_names[:tariffs_ids.index(tariff_id) + 1]
#
#    @transaction()
#    @authentificate
#    def get_tariff(self, data, operator, curs=None):
#        tariff = selector.get_tariff(curs, operator, data['name'])
#        tariffs_data = self._get_tariffs_data(curs, operator, [tariff])
#        return response_ok(**tariffs_data[0])
#
#    @transaction()
#    @authentificate
#    def get_tariff_detailed(self, data, operator, curs=None):
#        tariff = selector.get_tariff(curs, operator, data['name'])
#        tariffs_data = self._get_tariffs_data(curs, operator, [tariff])
#        tariff_data = tariffs_data[0]
#        types = selector.get_service_types_by_service_set(curs, operator, tariff_data['service_set'])
#        tariff_data['service_types'] = sorted([t.name for t in types])
#        return response_ok(**tariff_data)
#
#    @transaction()
#    @authentificate
#    def view_tariffs(self, _, operator, curs=None):
#        tariffs = mapping.get_list(curs, Tariff, cond=Eq('operator_id', operator.id))
#        return response_ok(tariffs=self._get_tariffs_data(curs, operator, tariffs))
#
#    @transaction()
#    @authentificate
#    def view_tariffs_detailed(self, _, operator, curs=None):
#        tariffs = mapping.get_list(curs, Tariff, cond=Eq('operator_id', operator.id))
#        service_sets_types = self._get_service_sets_types_dict(curs, operator)
#        tariffs_data = self._get_tariffs_data(curs, operator, tariffs)
#        for d in tariffs_data:
#            d['service_types'] = service_sets_types[d['service_set']]
#        return response_ok(tariffs=tariffs_data)
#
#    # rule
#    def _check_service_type_in_service_set(self, curs, service_type, service_set):
#        if service_type.id not in selector.get_service_types_ids(curs, [service_set.id]):
#            raise ServiceTypeNotInServiceSet(service_type.name, service_set.name)
#
#    @transaction()
#    @authentificate
#    @detalize_error(RuleError, RequestProcessingError.Category.data_invalid, 'rule')
#    @detalize_error(PriceProcessingError, RequestProcessingError.Category.data_invalid, 'rule')
#    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.data_invalid, 'service_type')
#    @detalize_error(ServiceTypeNotInServiceSet, RequestProcessingError.Category.data_invalid, 'service_type')
#    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
#    def save_draft_rule(self, data, operator, curs=None):
#        r_text = data['rule']
#        st_name = data['service_type']
#        enabled = data['enabled']
#        t_name = data['tariff']
#
#        tariff = selector.get_tariff(curs, operator, t_name)
#        service_set = selector.get_service_set(curs, tariff.service_set_id)
#        service_type = selector.get_service_type(curs, operator, st_name)
#
#        self._check_service_type_in_service_set(curs, service_type, service_set)
#        RuleChecker().check(r_text)
#
#        data['tariff_id'] = tariff.id
#        data['service_type_id'] = service_type.id
#        del data['tariff']
#        del data['service_type']
#        try:
#            rule = selector.get_rule(curs, tariff, service_type, Rule.TYPE_DRAFT, for_update=True)
#            rule.enabled = enabled
#            rule.rule = r_text
#            mapping.update(curs, rule)
#        except RuleNotFound:
#            data['type'] = Rule.TYPE_DRAFT
#            mapping.insert(curs, Rule(**data))
#        return response_ok()
#
#    @transaction()
#    @authentificate
#    @detalize_error(RuleNotFound, RequestProcessingError.Category.data_invalid, 'service_type')
#    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.data_invalid, 'service_type')
#    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
#    def delete_draft_rule(self, data, operator, curs=None):
#        t_name = data['tariff']
#        st_name = data['service_type']
#
#        tariff = selector.get_tariff(curs, operator, t_name)
#        service_type = selector.get_service_type(curs, operator, st_name)
#        rule = selector.get_rule(curs, tariff, service_type, Rule.TYPE_DRAFT, for_update=True)
#        mapping.delete(curs, rule)
#
#        return response_ok()
#
#    @transaction()
#    @authentificate
#    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
#    def make_draft_rules_actual(self, data, operator, curs=None):
#        t_name = data['tariff']
#        tariff = selector.get_tariff(curs, operator, t_name)
#        all_rules = selector.get_rules(curs, tariff, [Rule.TYPE_DRAFT, Rule.TYPE_ACTUAL], for_update=True)
#        draft_rules = filter(lambda x: x.type == Rule.TYPE_DRAFT, all_rules)
#        draft_st_ids = [r.service_type_id for r in draft_rules]
#        deleting_rules = filter(lambda x: x.type == Rule.TYPE_ACTUAL and x.service_type_id in draft_st_ids, all_rules)
#        q_del = mapping.Delete(Rule.table, cond=In('id', [r.id for r in deleting_rules]))
#        curs.execute(*q_del.glue())
#        q_upd = mapping.Update(Rule.table, {'type': Rule.TYPE_ACTUAL}, cond=In('id', [r.id for r in draft_rules]))
#        curs.execute(*q_upd.glue())
#        return response_ok()
#
#    @transaction()
#    @authentificate
#    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.data_invalid, 'service_type')
#    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
#    def modify_actual_rule(self, data, operator, curs=None):
#        t_name = data['tariff']
#        st_name = data['service_type']
#        tariff = selector.get_tariff(curs, operator, t_name)
#        service_type = selector.get_service_type(curs, operator, st_name)
#        loader = partial(selector.get_rule, curs, tariff, service_type, rule_type=Rule.TYPE_ACTUAL,
#            for_update=True)
#        self.update_obj(curs, data, loader)
#        return response_ok()
#
#    @transaction()
#    @authentificate
#    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.data_invalid, 'service_type')
#    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
#    @detalize_error(RuleNotFound, RequestProcessingError.Category.data_invalid, 'type')
#    def get_rule(self, data, operator, curs=None):
#        t_name = data['tariff']
#        st_name = data['service_type']
#        rule_type = data['type']
#        tariff = selector.get_tariff(curs, operator, t_name)
#        service_type = selector.get_service_type(curs, operator, st_name)
#        rule = selector.get_rule(curs, tariff, service_type, rule_type)
#        return response_ok(tariff=tariff.name, service_type=service_type.name, rule=rule.rule,
#            type=rule.type, enabled=rule.enabled)
#
#    @transaction()
#    @authentificate
#    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
#    def view_rules(self, data, operator, curs=None):
#        t_name = data['tariff']
#        tariff = selector.get_tariff(curs, operator, t_name)
#        st_names_idx = selector.get_service_types_names_indexed_by_id(curs, operator)
#        rules = []
#        for rule in selector.get_rules(curs, tariff, [Rule.TYPE_ACTUAL, Rule.TYPE_DRAFT]):
#            rules.append({
#                'service_type': st_names_idx[rule.service_type_id],
#                'rule': rule.rule,
#                'type': rule.type,
#                'enabled': rule.enabled,
#            })
#        return response_ok(tariff=tariff.name, rules=rules)
#
#    # price
#    def _calculate_tariffs_chain(self, tariff_id, tariffs_names_idx, parents_names_idx):
#        '''
#        @return: tariffs chain for tariff.name as [(tariff_id, tariff_name)]
#        '''
#        tariffs_chain = []
#        tariffs_ids_set = set()
#        while True:
#            if tariff_id is None:
#                break
#            if tariff_id in tariffs_ids_set:
#                raise TariffCycleError('Tariff cycle found in chain: %s' %
#                    ', '.join([n for (_, n) in tariffs_chain]))
#            tariffs_chain.append((tariff_id, tariffs_names_idx[tariff_id]))
#            tariffs_ids_set.add(tariff_id)
#            tariff_id = parents_names_idx[tariff_id]
#        return tariffs_chain
#
#    def _get_tariffs_chain(self, curs, operator, tariff_name):
#        '''
#        @return: tariffs chain for tariff_name as [(tariff_id, tariff_name)]
#        '''
#        return self._calculate_tariffs_chain(
#            selector.get_tariff(curs, operator, tariff_name).id,
#            selector.get_tariffs_names_indexed_by_id(curs, operator),
#            selector.get_tariffs_parent_ids_indexed_by_id(curs, operator)
#        )
#
#    def _find_nearest_rules_pair(self, indexed_rules, tariffs_ids, service_type_id):
#        '''
#        Finds first rules implementation in tariffs listed in tariffs_ids.
#        @return: (actual_rule, drart_rule)
#        '''
#        def find_rule(rule_type):
#            for t_id in tariffs_ids:
#                k = (t_id, service_type_id, rule_type)
#                if k in indexed_rules:
#                    return indexed_rules[k]
#            return None
#        return  find_rule(Rule.TYPE_ACTUAL), find_rule(Rule.TYPE_DRAFT)
#
#    def _get_price_info(self, rule, ctx, t_ids, t_names):
#        if rule is None:
#            return {
#                'price': None,
#                'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
#                'tariffs_chain': t_names,
#            }
#        elif not rule.enabled:
#            return {
#                'price': None,
#                'price_calculation': PRICE_CALC_RULE_DISABLED,
#                'tariffs_chain': self._tariffs_chain_names(rule.tariff_id, t_ids, t_names),
#            }
#
#        try:
#            price = engine.process(RequestPrice(rule, ctx)).price
#            return {
#                'price': format_price(price),
#                'price_calculation': PRICE_CALC_NORMAL,
#                'tariffs_chain': self._tariffs_chain_names(rule.tariff_id, t_ids, t_names),
#            }
#        except (PriceProcessingError, RuleError):
#            return {
#                'price': None,
#                'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
#                'tariffs_chain': self._tariffs_chain_names(rule.tariff_id, t_ids, t_names),
#            }
#
#
#    @transaction()
#    @authentificate
#    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
#    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.data_invalid, 'service_type')
#    def get_price(self, data, operator, curs=None):
#        t_name = data['tariff']
#        ctx = data.get('context', {})
#        st_name = data['service_type']
#
#        t_chain = self._get_tariffs_chain(curs, operator, t_name)
#        t_ids, t_names = map(list, zip(*t_chain))
#
#        st = selector.get_service_type(curs, operator, st_name)
#        rules_idx = selector.get_rules_indexed_by_tariff_service_type_ids(curs, operator, t_ids,
#            [st.id])
#        response = {}
#        response['tariff'] = t_name
#        response['service_type'] = st_name
#        response['context'] = ctx
#
#        actual_rule, draft_rule = self._find_nearest_rules_pair(rules_idx, t_ids, st.id)
#
#        actual_r_info = self._get_price_info(actual_rule, ctx, t_ids, t_names)
#        response.update(actual_r_info)
#
#        draft_r_info = self._get_price_info(draft_rule, ctx, t_ids, t_names).items()
#        draft_r_info = dict([('draft_%s' % k, v) for (k, v) in draft_r_info])
#        response.update(draft_r_info)
#
#        return response_ok(**response)
#
#    @transaction()
#    @authentificate
#    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
#    def view_prices(self, data, operator, curs=None):
#        t_name = data['tariff']
#        ctx = data.get('context', {})
#
#        t_chain = self._get_tariffs_chain(curs, operator, t_name)
#        t_ids, t_names = map(list, zip(*t_chain))
#
#        ss_ids = selector.get_service_sets_ids(curs, t_ids)
#        st_ids = selector.get_service_types_ids(curs, ss_ids)
#
#        rules_idx = selector.get_rules_indexed_by_tariff_service_type_ids(curs, operator, t_ids, st_ids)
#        st_names_idx = selector.get_service_types_names_indexed_by_id(curs, operator)
#
#        response = {}
#        response['tariff'] = t_name
#        response['context'] = ctx
#        response['prices'] = []
#
#        prices = response['prices']
#        for st_id in st_ids:
#            p_info = {'service_type': st_names_idx[st_id]}
#            actual_rule, draft_rule = self._find_nearest_rules_pair(rules_idx, t_ids, st_id)
#
#            actual_r_info = self._get_price_info(actual_rule, ctx, t_ids, t_names)
#            p_info.update(actual_r_info)
#
#            draft_r_info = self._get_price_info(draft_rule, ctx, t_ids, t_names).items()
#            draft_r_info = dict([('draft_%s' % k, v) for (k, v) in draft_r_info])
#            p_info.update(draft_r_info)
#
#            prices.append(p_info)
#        return response_ok(**response)
#
#    @transaction()
#    @authentificate
#    def view_action_logs(self, data, operator, curs=None):
#        al_info = []
#        action_logs = selector.get_action_logs(curs, operator, data['filter_params'])
#        for action_log in action_logs:
#            al_info.append({
#                'custom_operator_info': action_log.custom_operator_info,
#                'action': action_log.action,
#                'request_date': action_log.request_date.isoformat(),
#                'remote_addr': action_log.remote_addr,
#                'request': action_log.request,
#                'response': action_log.response,
#            })
#        total = selector.get_action_logs_count(curs, operator, data['filter_params'])
#        return response_ok(total=int(total), action_logs=al_info)
