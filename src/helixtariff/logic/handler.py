from functools import partial

import helixcore.mapping.actions as mapping
from helixcore.db.sql import Eq, In, And
from helixcore.server.response import response_ok
from helixcore.db.wrapper import EmptyResultSetError, ObjectAlreadyExists
from helixcore.server.errors import RequestProcessingError
from helixcore.server.exceptions import AuthError

from helixtariff.conf.db import transaction
from helixtariff.domain.objects import (Client, ServiceType,
    ServiceSet, ServiceSetRow, Tariff, Rule)
from helixtariff.logic import selector
from helixtariff.rulesengine.checker import RuleChecker, RuleError
from helixtariff.rulesengine import engine
from helixtariff.rulesengine.interaction import (RequestPrice,
    PriceProcessingError)
from helixtariff.domain import security
from helixtariff.error import (TariffCycleError, ServiceTypeNotFound,
    ServiceSetNotEmpty, ServiceTypeUsed, TariffUsed, RuleNotFound,
    ServiceSetNotFound, TariffNotFound, ServiceTypeNotInServiceSet,
    ServiceSetUsed)
from helixtariff.validator.validator import (PRICE_CALC_NORMAL,
    PRICE_CALC_PRICE_UNDEFINED, PRICE_CALC_RULE_DISABLED)
from helixtariff.utils import format_price


def detalize_error(err_cls, category, f_name):
    def decorator(func):
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except err_cls, e:
                raise RequestProcessingError(category, e.message,
                    details=[{'field': f_name, 'message': e.message}])
        return decorated
    return decorator


@detalize_error(AuthError, RequestProcessingError.Category.auth, 'login')
def authentificate(method):
    def decroated(self, data, curs):
        data['client_id'] = self.get_client_id(curs, data)
        del data['login']
        del data['password']
        data.pop('custom_client_info', None)
        return method(self, data, curs)
    return decroated


class Handler(object):
    '''Handles all API actions. Method names are called like actions.'''
    def ping(self, _):
        return response_ok()

    def get_client_id(self, curs, data):
        return selector.get_auth_client(curs, data['login'], data['password']).id

    def get_fields_for_update(self, data, prefix_of_new='new_'):
        '''
        If data contains fields with previx == prefix_of_new,
        such fields will be added into result dict:
            {'field': 'new_field'}
        '''
        result = {}
        for f in data.keys():
            if f.startswith(prefix_of_new):
                result[f[len(prefix_of_new):]] = f
        return result

    def update_obj(self, curs, data, load_obj_func):
        to_update = self.get_fields_for_update(data)
        if len(to_update):
            obj = load_obj_func()
            for f, new_f in to_update.items():
                setattr(obj, f, data[new_f])
            mapping.update(curs, obj)

    # client
    @detalize_error(ObjectAlreadyExists, RequestProcessingError.Category.data_integrity, 'login')
    @transaction()
    def add_client(self, data, curs=None):
        data['password'] = security.encrypt_password(data['password'])
        data.pop('custom_client_info', None)
        mapping.insert(curs, Client(**data))
        return response_ok()

    @transaction()
    @authentificate
    def modify_client(self, data, curs=None):
        if 'new_password' in data:
            data['new_password'] = security.encrypt_password(data['new_password'])
        loader = partial(selector.get_client, curs, data['client_id'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    # server_type
    @transaction()
    @authentificate
    @detalize_error(ObjectAlreadyExists, RequestProcessingError.Category.data_integrity, 'name')
    def add_service_type(self, data, curs=None):
        mapping.insert(curs, ServiceType(**data))
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.auth, 'name')
    def modify_service_type(self, data, curs=None):
        loader = partial(selector.get_service_type, curs, data['client_id'], data['name'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.auth, 'name')
    @detalize_error(ServiceTypeUsed, RequestProcessingError.Category.auth, 'name')
    def delete_service_type(self, data, curs=None):
        c_id = data['client_id']
        st_name = data['name']
        t = selector.get_service_type(curs, c_id, st_name, for_update=True)
        ss_ids = selector.get_service_sets_ids_by_service_type(curs, t)
        if ss_ids:
            ss_names_idx = selector.get_service_sets_names_indexed_by_id(curs, c_id)
            ss_names = [ss_names_idx[idx] for idx in ss_ids]
            raise ServiceTypeUsed('''Service type '%s' used in service sets %s''' %
                (st_name, ss_names))
        mapping.delete(curs, t)
        return response_ok()

    @transaction()
    @authentificate
    def view_service_types(self, data, curs=None):
        service_types = selector.get_service_types(curs, data['client_id'])
        return response_ok(
            service_types=[t.name for t in service_types]
        )

    @transaction()
    @authentificate
    def view_service_types_detailed(self, data, curs=None):
        c_id = data['client_id']
        service_types = selector.get_service_types(curs, c_id)
        # {service_type_id: [service_set_id, ...]}
        st_info_idx = {}
        for row in selector.get_service_set_rows_by_service_types(curs, service_types):
            st_id = row.service_type_id
            if st_id not in st_info_idx:
                st_info_idx[st_id] = []
            st_info_idx[st_id].append(row.service_set_id)

        ss_names_idx = selector.get_service_sets_names_indexed_by_id(curs, c_id)
        st_info_list = []
        for service_type in service_types:
            ss_ids = st_info_idx.get(service_type.id, [])
            ss_names = sorted([ss_names_idx[ss_id] for ss_id in ss_ids])
            st_info_list.append(
                {'name': service_type.name, 'service_sets': ss_names}
            )
        return response_ok(service_types=st_info_list)

    def _set_service_types_to_service_set(self, curs, client_id, service_set, service_types_names):
        curs.execute(*mapping.Delete(ServiceSetRow.table, cond=Eq('service_set_id', service_set.id)).glue())
        st_names_idx = selector.get_service_types_names_indexed_by_id(curs, client_id)
        st_ids_idx = dict([(v, k) for (k, v) in st_names_idx.items()])

        not_found_st_names = filter(lambda x: x not in st_ids_idx, service_types_names)
        if not_found_st_names:
            raise ServiceTypeNotFound(', '.join(not_found_st_names))

        ids_to_set = [st_ids_idx[n] for n in service_types_names]

        for t_id in ids_to_set:
            mapping.insert(curs, ServiceSetRow(service_set_id=service_set.id, service_type_id=t_id))

    @transaction()
    @authentificate
    @detalize_error(ObjectAlreadyExists, RequestProcessingError.Category.data_integrity, 'name')
    def add_service_set(self, data, curs=None):
        service_types_names = data['service_types']
        del data['service_types']
        client_id = data['client_id']

        service_set = ServiceSet(**data)
        mapping.insert(curs, service_set)
        self._set_service_types_to_service_set(curs, client_id, service_set, service_types_names)

        return response_ok()

    def _check_types_not_used(self, curs, client_id, service_sets_ids, service_types_names):
        service_types_names_idx = selector.get_service_types_names_indexed_by_id(curs, client_id)
        service_types_ids_idx = dict([(v, k) for (k, v) in service_types_names_idx.items()])
        tariffs = selector.get_tariffs_binded_with_service_sets(curs, client_id, service_sets_ids)
        cond_t_ids = In('tariff_id', [t.id for t in tariffs])
        cond_st_ids = In('service_type_id', [service_types_ids_idx[n] for n in service_types_names])
        rules = mapping.get_list(curs, Rule, cond=And(cond_t_ids, cond_st_ids))
        if rules:
            tariffs_names_idx = dict([(t.id, t.name) for t in tariffs])
            usage = {}
            for r in rules:
                tariff_name = tariffs_names_idx[r.tariff_id]
                if tariff_name not in usage:
                    usage[tariff_name] = []
                usage[tariff_name].append(service_types_names_idx[r.service_type_id])
            raise ServiceTypeUsed('Service types %s used in %s' % (service_types_names, usage))

    @transaction()
    @authentificate
    @detalize_error(ServiceSetNotFound, RequestProcessingError.Category.auth, 'name')
    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.data_integrity, 'service_types')
    def modify_service_set(self, data, curs=None):
        client_id = data['client_id']
        service_set = selector.get_service_set_by_name(curs, data['client_id'],
            data['name'], for_update=True)
        def loader():
            return service_set
        if 'new_service_types' in data:
            old_service_types_names = [t.name for t in selector.get_service_types_by_service_set(curs, client_id, service_set.name)]
            service_types_names = data['new_service_types']
            service_types_names_to_check = list(set(old_service_types_names) - set(service_types_names))
            self._check_types_not_used(curs, client_id, [service_set.id], service_types_names_to_check)
            del data['new_service_types']
            self._set_service_types_to_service_set(curs, client_id, service_set, service_types_names)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(ServiceSetNotFound, RequestProcessingError.Category.auth, 'name')
    @detalize_error(ServiceSetUsed, RequestProcessingError.Category.auth, 'name')
    def delete_service_set(self, data, curs=None):
        c_id = data['client_id']
        ss_name = data['name']
        service_set = selector.get_service_set_by_name(curs, c_id, ss_name, for_update=True)
        if selector.get_service_set_rows(curs, [service_set.id]):
            raise ServiceSetNotEmpty(service_set.name)
        used_in_tariffs = selector.get_tariffs_binded_with_service_sets(curs, c_id, [service_set.id])
        if used_in_tariffs:
            raise ServiceSetUsed(used_in_tariffs)
        mapping.delete(curs, service_set)
        return response_ok()

    def _get_service_set_info(self, curs, client_id, service_set_name):
        service_set = selector.get_service_set_by_name(curs, client_id, service_set_name)
        service_types = selector.get_service_types_by_service_set(curs, client_id, service_set.name)
        return service_set, service_types

    def _process_service_set_row(self, curs, service_set, types_names, func):
        for n in types_names:
            try:
                t = selector.get_service_type(curs, service_set.client_id, n)
                s = ServiceSetRow(**{'service_type_id': t.id, 'service_set_id': service_set.id})
                func(curs, s)
            except EmptyResultSetError, _:
                raise ServiceTypeNotFound(n)

    def _get_service_sets_types_dict(self, curs, client_id):
        '''
        @return: dictionary {service_set_name: [types_names]}
        '''
        t_names = selector.get_service_types_names_indexed_by_id(curs, client_id)
        ss_names = selector.get_service_sets_names_indexed_by_id(curs, client_id)
        ss_rows = selector.get_service_set_rows(curs, ss_names.keys())
        service_sets_info = {}
        for n in ss_names.values():
            service_sets_info[n] = list()
        for ss_row in ss_rows:
            ss_name = ss_names[ss_row.service_set_id]
            t_name = t_names[ss_row.service_type_id]
            service_sets_info[ss_name].append(t_name)
        for l in service_sets_info.values():
            l.sort()
        return service_sets_info

    @transaction()
    @authentificate
    def get_service_set(self, data, curs=None):
        service_set, service_types = self._get_service_set_info(curs, data['client_id'], data['name'])
        return response_ok(
            name=service_set.name,
            service_types=sorted([t.name for t in service_types])
        )

    @transaction()
    @authentificate
    def get_service_set_detailed(self, data, curs=None):
        c_id = data['client_id']
        ss_name = data['name']
        ss, s_types = self._get_service_set_info(curs, c_id, ss_name)
        ts = selector.get_tariffs_binded_with_service_sets(curs, c_id, [ss.id])
        return response_ok(
            name=ss.name,
            service_types=sorted([st.name for st in s_types]),
            tariffs=sorted([t.name for t in ts])
        )

    @transaction()
    @authentificate
    def view_service_sets(self, data, curs=None):
        c_id = data['client_id']
        ss_types = self._get_service_sets_types_dict(curs, c_id)
        result = []
        for n in sorted(ss_types.keys()):
            result.append({'name': n, 'service_types': sorted(ss_types[n])})
        return response_ok(service_sets=result)

    @transaction()
    @authentificate
    def view_service_sets_detailed(self, data, curs=None):
        c_id = data['client_id']
        ss_names_idx = selector.get_service_sets_names_indexed_by_id(curs, c_id)
        ss_ids_idx = dict([(v, k) for (k, v) in ss_names_idx.items()])
        ss_with_types = self._get_service_sets_types_dict(curs, c_id)
        ss_ids = [ss_ids_idx[n] for n in sorted(ss_with_types.keys())]
        tariffs = selector.get_tariffs_binded_with_service_sets(curs, c_id, ss_ids)
        result = []
        for ss_id in ss_ids:
            ss_name = ss_names_idx[ss_id]
            result.append({
                'name': ss_name,
                'service_types': sorted(ss_with_types[ss_name]),
                'tariffs': sorted([t.name for t in filter(lambda x: x.service_set_id == ss_id, tariffs)]),
            })
        return response_ok(service_sets=result)

    # tariff
    @transaction()
    @authentificate
    @detalize_error(ObjectAlreadyExists, RequestProcessingError.Category.data_integrity, 'name')
    @detalize_error(ServiceSetNotFound, RequestProcessingError.Category.data_integrity, 'service_set')
    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_integrity, 'parent_tariff')
    def add_tariff(self, data, curs=None):
        service_set = selector.get_service_set_by_name(curs, data['client_id'], data['service_set'])
        del data['service_set']
        data['service_set_id'] = service_set.id
        parent_tariff = data['parent_tariff']
        if parent_tariff is None:
            parent_id = None
        else:
            parent_id = selector.get_tariff(curs, data['client_id'], parent_tariff).id
        del data['parent_tariff']
        data['parent_id'] = parent_id
        mapping.insert(curs, Tariff(**data))
        return response_ok()

    def _get_new_parent_id(self, curs, client_id, tariff_name, new_parent_name):
        if new_parent_name is None:
            return None
        tariffs_names_idx = selector.get_tariffs_names_indexed_by_id(curs, client_id)
        tariffs_ids_idx = dict([(v, k) for (k, v) in tariffs_names_idx.iteritems()])

        if tariff_name not in tariffs_ids_idx:
            raise TariffNotFound(tariff_name)
        tariff_id = tariffs_ids_idx[tariff_name]

        if new_parent_name not in tariffs_ids_idx:
            raise TariffNotFound(new_parent_name)
        new_parent_id = tariffs_ids_idx[new_parent_name]

        parents_ids_idx = selector.get_tariffs_parent_ids_indexed_by_id(curs, client_id)
        parents_ids_idx[tariff_id] = new_parent_id
        self._calculate_tariffs_chain(
            tariff_id,
            tariffs_names_idx,
            parents_ids_idx
        )
        return new_parent_id

    @transaction()
    @authentificate
    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_integrity, 'name')
    @detalize_error(TariffCycleError, RequestProcessingError.Category.data_integrity, 'parent_tariff')
    @detalize_error(ServiceSetNotFound, RequestProcessingError.Category.data_integrity, 'service_set')
    def modify_tariff(self, data, curs=None):
        c_id = data['client_id']
        t_name = data['name']
        t = selector.get_tariff(curs, c_id, t_name, for_update=True)
        if 'new_parent_tariff' in data:
            new_p_name = data['new_parent_tariff']
            try:
                data['new_parent_id'] = self._get_new_parent_id(curs, c_id, t_name, new_p_name)
            except TariffNotFound, e:
                raise RequestProcessingError(RequestProcessingError.Category.data_integrity,
                    e.message, details={'parent_tariff': e.message})
            del data['new_parent_tariff']
        if 'new_service_set' in data:
            new_ss = selector.get_service_set_by_name(curs, c_id, data['new_service_set'])
            st_names_idx = selector.get_service_types_names_indexed_by_id(curs, c_id)
            old_st_ids = selector.get_service_types_ids(curs, [t.service_set_id])
            new_st_ids = selector.get_service_types_ids(curs, [new_ss.id])
            st_names_to_check = [st_names_idx[idx] for idx in set(old_st_ids) - set(new_st_ids)]
            self._check_types_not_used(curs, c_id, [new_ss.id], st_names_to_check)
            data['new_service_set_id'] = new_ss.id
            del data['new_service_set']
        def loader():
            return t
        self.update_obj(curs, data, loader)
        return response_ok()


    @transaction()
    @authentificate
    @detalize_error(TariffUsed, RequestProcessingError.Category.data_integrity, 'name')
    def delete_tariff(self, data, curs=None):
        c_id = data['client_id']
        t_name = data['name']
        t = selector.get_tariff(curs, c_id, t_name, for_update=True)
        childs = selector.get_child_tariffs(curs, t)
        if childs:
            raise TariffUsed('''Tariff '%s' is parent of %s''' % (t.name, [t.name for t in childs]))
        rules = selector.get_rules(curs, t, [Rule.TYPE_ACTUAL, Rule.TYPE_DRAFT])
        undel_rules = filter(lambda x: x.type == Rule.TYPE_ACTUAL and x.enabled, rules)
        if undel_rules:
            st_names_idx = selector.get_service_sets_names_indexed_by_id(curs, c_id)
            raise TariffUsed('''In tariff '%s' defined rules for services %s''' %
                (t.name, [st_names_idx[r.service_type_id] for r in undel_rules]))
        else:
            mapping.delete_objects(curs, rules)
        mapping.delete(curs, t)
        return response_ok()

    def _get_tariffs_data(self, curs, c_id, tariffs):
        ss_names = selector.get_service_sets_names_indexed_by_id(curs, c_id)
        t_names_idx = selector.get_tariffs_names_indexed_by_id(curs, c_id)
        pt_ids_idx = selector.get_tariffs_parent_ids_indexed_by_id(curs, c_id)

        result = []
        for tariff in tariffs:
            t_chain = self._calculate_tariffs_chain(tariff.id, t_names_idx, pt_ids_idx)
            _, t_names = map(list, zip(*t_chain))
            try:
                pt_name = t_names[1]
            except IndexError:
                pt_name = None

            result.append(
                {
                    'name': tariff.name,
                    'service_set': ss_names.get(tariff.service_set_id),
                    'tariffs_chain': t_names,
                    'parent_tariff': pt_name,
                    'in_archive': tariff.in_archive,
                }
            )
        return result

    def _tariffs_chain_names(self, tariff_id, tariffs_ids, tariffs_names):
        return tariffs_names[:tariffs_ids.index(tariff_id) + 1]

    @transaction()
    @authentificate
    def get_tariff(self, data, curs=None):
        client_id = data['client_id']
        tariff = selector.get_tariff(curs, client_id, data['name'])
        tariffs_data = self._get_tariffs_data(curs, client_id, [tariff])
        return response_ok(**tariffs_data[0])

    @transaction()
    @authentificate
    def get_tariff_detailed(self, data, curs=None):
        client_id = data['client_id']
        tariff = selector.get_tariff(curs, client_id, data['name'])
        tariffs_data = self._get_tariffs_data(curs, client_id, [tariff])
        tariff_data = tariffs_data[0]
        types = selector.get_service_types_by_service_set(curs, client_id, tariff_data['service_set'])
        tariff_data['service_types'] = sorted([t.name for t in types])
        return response_ok(**tariff_data)

    @transaction()
    @authentificate
    def view_tariffs(self, data, curs=None):
        client_id = data['client_id']
        tariffs = mapping.get_list(curs, Tariff, cond=Eq('client_id', client_id))
        return response_ok(tariffs=self._get_tariffs_data(curs, client_id, tariffs))

    @transaction()
    @authentificate
    def view_tariffs_detailed(self, data, curs=None):
        client_id = data['client_id']
        tariffs = mapping.get_list(curs, Tariff, cond=Eq('client_id', client_id))
        service_sets_types = self._get_service_sets_types_dict(curs, client_id)
        tariffs_data = self._get_tariffs_data(curs, client_id, tariffs)
        for d in tariffs_data:
            d['service_types'] = service_sets_types[d['service_set']]
        return response_ok(tariffs=tariffs_data)

    # rule
    def _check_service_type_in_service_set(self, curs, service_type, service_set):
        if service_type.id not in selector.get_service_types_ids(curs, [service_set.id]):
            raise ServiceTypeNotInServiceSet(service_type.name, service_set.name)

    @transaction()
    @authentificate
    @detalize_error(RuleError, RequestProcessingError.Category.data_invalid, 'rule')
    @detalize_error(PriceProcessingError, RequestProcessingError.Category.data_invalid, 'rule')
    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.data_invalid, 'service_type')
    @detalize_error(ServiceTypeNotInServiceSet, RequestProcessingError.Category.data_invalid, 'service_type')
    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
    def save_draft_rule(self, data, curs=None):
        c_id = data['client_id']
        r_text = data['rule']
        st_name = data['service_type']
        enabled = data['enabled']
        t_name = data['tariff']

        tariff = selector.get_tariff(curs, c_id, t_name)
        service_set = selector.get_service_set(curs, tariff.service_set_id)
        service_type = selector.get_service_type(curs, c_id, st_name)

        self._check_service_type_in_service_set(curs, service_type, service_set)
        RuleChecker().check(r_text)

        data['tariff_id'] = tariff.id
        data['service_type_id'] = service_type.id
        del data['tariff']
        del data['service_type']
        try:
            rule = selector.get_rule(curs, tariff, service_type, Rule.TYPE_DRAFT, for_update=True)
            rule.enabled = enabled
            rule.rule = r_text
            mapping.update(curs, rule)
        except RuleNotFound:
            data['type'] = Rule.TYPE_DRAFT
            mapping.insert(curs, Rule(**data))
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(RuleNotFound, RequestProcessingError.Category.data_invalid, 'service_type')
    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.data_invalid, 'service_type')
    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
    def delete_draft_rule(self, data, curs=None):
        c_id = data['client_id']
        t_name = data['tariff']
        st_name = data['service_type']

        tariff = selector.get_tariff(curs, c_id, t_name)
        service_type = selector.get_service_type(curs, c_id, st_name)
        rule = selector.get_rule(curs, tariff, service_type, Rule.TYPE_DRAFT, for_update=True)
        mapping.delete(curs, rule)

        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
    def make_draft_rules_actual(self, data, curs=None):
        c_id = data['client_id']
        t_name = data['tariff']
        tariff = selector.get_tariff(curs, c_id, t_name)
        all_rules = selector.get_rules(curs, tariff, [Rule.TYPE_DRAFT, Rule.TYPE_ACTUAL], for_update=True)
        draft_rules = filter(lambda x: x.type == Rule.TYPE_DRAFT, all_rules)
        draft_st_ids = [r.service_type_id for r in draft_rules]
        deleting_rules = filter(lambda x: x.type == Rule.TYPE_ACTUAL and x.service_type_id in draft_st_ids, all_rules)
        q_del = mapping.Delete(Rule.table, cond=In('id', [r.id for r in deleting_rules]))
        curs.execute(*q_del.glue())
        q_upd = mapping.Update(Rule.table, {'type': Rule.TYPE_ACTUAL}, cond=In('id', [r.id for r in draft_rules]))
        curs.execute(*q_upd.glue())
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.data_invalid, 'service_type')
    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
    def modify_actual_rule(self, data, curs=None):
        c_id = data['client_id']
        t_name = data['tariff']
        st_name = data['service_type']
        tariff = selector.get_tariff(curs, c_id, t_name)
        service_type = selector.get_service_type(curs, c_id, st_name)
        loader = partial(selector.get_rule, curs, tariff, service_type, rule_type=Rule.TYPE_ACTUAL,
            for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.data_invalid, 'service_type')
    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
    @detalize_error(RuleNotFound, RequestProcessingError.Category.data_invalid, 'type')
    def get_rule(self, data, curs=None):
        c_id = data['client_id']
        t_name = data['tariff']
        st_name = data['service_type']
        rule_type = data['type']
        tariff = selector.get_tariff(curs, c_id, t_name)
        service_type = selector.get_service_type(curs, c_id, st_name)
        rule = selector.get_rule(curs, tariff, service_type, rule_type)
        return response_ok(tariff=tariff.name, service_type=service_type.name, rule=rule.rule,
            type=rule.type, enabled=rule.enabled)

    @transaction()
    @authentificate
    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
    def view_rules(self, data, curs=None):
        c_id = data['client_id']
        t_name = data['tariff']
        tariff = selector.get_tariff(curs, c_id, t_name)
        st_names_idx = selector.get_service_types_names_indexed_by_id(curs, c_id)
        rules = []
        for rule in selector.get_rules(curs, tariff, [Rule.TYPE_ACTUAL, Rule.TYPE_DRAFT]):
            rules.append({
                'service_type': st_names_idx[rule.service_type_id],
                'rule': rule.rule,
                'type': rule.type,
                'enabled': rule.enabled,
            })
        return response_ok(tariff=tariff.name, rules=rules)

    # price
    def _calculate_tariffs_chain(self, tariff_id, tariffs_names_idx, parents_names_idx):
        '''
        @return: tariffs chain for tariff.name as [(tariff_id, tariff_name)]
        '''
        tariffs_chain = []
        tariffs_ids_set = set()
        while True:
            if tariff_id is None:
                break
            if tariff_id in tariffs_ids_set:
                raise TariffCycleError('Tariff cycle found in chain: %s' %
                    ', '.join([n for (_, n) in tariffs_chain]))
            tariffs_chain.append((tariff_id, tariffs_names_idx[tariff_id]))
            tariffs_ids_set.add(tariff_id)
            tariff_id = parents_names_idx[tariff_id]
        return tariffs_chain

    def _get_tariffs_chain(self, curs, client_id, tariff_name):
        '''
        @return: tariffs chain for tariff_name as [(tariff_id, tariff_name)]
        '''
        return self._calculate_tariffs_chain(
            selector.get_tariff(curs, client_id, tariff_name).id,
            selector.get_tariffs_names_indexed_by_id(curs, client_id),
            selector.get_tariffs_parent_ids_indexed_by_id(curs, client_id)
        )

    def _find_nearest_rules_pair(self, indexed_rules, tariffs_ids, service_type_id):
        '''
        Finds first rules implementation in tariffs listed in tariffs_ids.
        @return: (actual_rule, drart_rule)
        '''
        def find_rule(rule_type):
            for t_id in tariffs_ids:
                k = (t_id, service_type_id, rule_type)
                if k in indexed_rules:
                    return indexed_rules[k]
            return None
        return  find_rule(Rule.TYPE_ACTUAL), find_rule(Rule.TYPE_DRAFT)

    def _get_price_info(self, rule, ctx, t_ids, t_names):
        if rule is None:
            return {
                'price': None,
                'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
                'tariffs_chain': t_names,
            }
        elif not rule.enabled:
            return {
                'price': None,
                'price_calculation': PRICE_CALC_RULE_DISABLED,
                'tariffs_chain': self._tariffs_chain_names(rule.tariff_id, t_ids, t_names),
            }

        try:
            price = engine.process(RequestPrice(rule, ctx)).price
            return {
                'price': format_price(price),
                'price_calculation': PRICE_CALC_NORMAL,
                'tariffs_chain': self._tariffs_chain_names(rule.tariff_id, t_ids, t_names),
            }
        except PriceProcessingError:
            return {
                'price': None,
                'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
                'tariffs_chain': self._tariffs_chain_names(rule.tariff_id, t_ids, t_names),
            }


    @transaction()
    @authentificate
    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
    @detalize_error(ServiceTypeNotFound, RequestProcessingError.Category.data_invalid, 'service_type')
    def get_price(self, data, curs=None):
        c_id = data['client_id']
        t_name = data['tariff']
        ctx = data.get('context', {})
        st_name = data['service_type']

        t_chain = self._get_tariffs_chain(curs, c_id, t_name)
        t_ids, t_names = map(list, zip(*t_chain))

        st = selector.get_service_type(curs, c_id, st_name)
        rules_idx = selector.get_rules_indexed_by_tariff_service_type_ids(curs, c_id, t_ids,
            [st.id])
        response = {}
        response['tariff'] = t_name
        response['service_type'] = st_name
        response['context'] = ctx

        actual_rule, draft_rule = self._find_nearest_rules_pair(rules_idx, t_ids, st.id)

        actual_r_info = self._get_price_info(actual_rule, ctx, t_ids, t_names)
        response.update(actual_r_info)

        draft_r_info = self._get_price_info(draft_rule, ctx, t_ids, t_names).items()
        draft_r_info = dict([('draft_%s' % k, v) for (k, v) in draft_r_info])
        response.update(draft_r_info)

        return response_ok(**response)

    @transaction()
    @authentificate
    @detalize_error(TariffNotFound, RequestProcessingError.Category.data_invalid, 'tariff')
    def view_prices(self, data, curs=None):
        c_id = data['client_id']
        t_name = data['tariff']
        ctx = data.get('context', {})

        t_chain = self._get_tariffs_chain(curs, c_id, t_name)
        t_ids, t_names = map(list, zip(*t_chain))

        ss_ids = selector.get_service_sets_ids(curs, t_ids)
        st_ids = selector.get_service_types_ids(curs, ss_ids)

        rules_idx = selector.get_rules_indexed_by_tariff_service_type_ids(curs, c_id, t_ids, st_ids)
        st_names_idx = selector.get_service_types_names_indexed_by_id(curs, c_id)

        response = {}
        response['tariff'] = t_name
        response['context'] = ctx
        response['prices'] = []

        prices = response['prices']
        for st_id in st_ids:
            p_info = {'service_type': st_names_idx[st_id]}
            actual_rule, draft_rule = self._find_nearest_rules_pair(rules_idx, t_ids, st_id)

            actual_r_info = self._get_price_info(actual_rule, ctx, t_ids, t_names)
            p_info.update(actual_r_info)

            draft_r_info = self._get_price_info(draft_rule, ctx, t_ids, t_names).items()
            draft_r_info = dict([('draft_%s' % k, v) for (k, v) in draft_r_info])
            p_info.update(draft_r_info)

            prices.append(p_info)
        return response_ok(**response)

    @transaction()
    @authentificate
    def view_action_logs(self, data, curs=None):
        c_id = data['client_id']
        al_info = []
        action_logs = selector.get_action_logs(curs, selector.get_client(curs, c_id), data['filter_params'])
        for action_log in action_logs:
            al_info.append({
                'custom_client_info': action_log.custom_client_info,
                'action': action_log.action,
                'request_date': action_log.request_date.isoformat(),
                'request': action_log.request,
                'response': action_log.response,
            })
        total = selector.get_action_logs_count(curs, selector.get_client(curs, c_id), data['filter_params'])
        return response_ok(total=int(total), action_logs=al_info)
