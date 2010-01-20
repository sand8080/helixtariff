from functools import partial

import helixcore.mapping.actions as mapping
from helixcore.db.sql import Eq, In, And
from helixcore.server.response import response_ok
from helixcore.db.wrapper import EmptyResultSetError

from helixtariff.conf.db import transaction
from helixtariff.domain.objects import Client, ServiceType, \
    ServiceSet, ServiceSetRow, Tariff, Rule
from helixtariff.logic import selector
from helixtariff.rulesengine.checker import RuleChecker
from helixtariff.rulesengine import engine
from helixtariff.rulesengine.interaction import RequestPrice
from helixtariff.domain import security
from helixtariff.error import TariffCycleError, ServiceTypeNotFound, RuleNotFound,\
    ServiceSetNotEmpty, ServiceTypeUsed


def authentificate(method):
    def decroated(self, data, curs):
        data['client_id'] = self.get_client_id(curs, data)
        del data['login']
        del data['password']
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
    @transaction()
    def add_client(self, data, curs=None):
        data['password'] = security.encrypt_password(data['password'])
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

    @transaction()
    @authentificate
    def delete_client(self, data, curs=None):
        obj = selector.get_client(curs, data['client_id'])
        mapping.delete(curs, obj)
        return response_ok()

    # server_type
    @transaction()
    @authentificate
    def add_service_type(self, data, curs=None):
        mapping.insert(curs, ServiceType(**data))
        return response_ok()

    @transaction()
    @authentificate
    def modify_service_type(self, data, curs=None):
        loader = partial(selector.get_service_type_by_name, curs, data['client_id'], data['name'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    def delete_service_type(self, data, curs=None):
        t = selector.get_service_type_by_name(curs, data['client_id'], data['name'], for_update=True)
        mapping.delete(curs, t)
        return response_ok()

    @transaction()
    @authentificate
    def view_service_types(self, data, curs=None):
        service_types = selector.get_service_types(curs, data['client_id'])
        return response_ok(
            service_types=[t.name for t in service_types]
        )

    # server_set
    def _set_service_types_to_service_set(self, curs, client_id, service_set, service_types_names):
        curs.execute(*mapping.Delete(ServiceSetRow.table, cond=Eq('service_set_id', service_set.id)).glue())
        service_types_names_idx = selector.get_service_types_names_indexed_by_id(curs, client_id)
        service_types_ids_idx = dict([(v, k) for (k, v) in service_types_names_idx.items()])
        ids_to_set = [service_types_ids_idx[n] for n in service_types_names]

        for t_id in ids_to_set:
            mapping.insert(curs, ServiceSetRow(service_set_id=service_set.id, service_type_id=t_id))

    @transaction()
    @authentificate
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
    def delete_service_set(self, data, curs=None):
        client_id = data['client_id']
        service_set = selector.get_service_set_by_name(curs, client_id, data['name'], for_update=True)
        if selector.get_service_set_rows(curs, [service_set.id]):
            raise ServiceSetNotEmpty(service_set.name)
        mapping.delete(curs, service_set)
        return response_ok()

    def _get_service_set_info(self, curs, client_id, service_set_name):
        service_set = selector.get_service_set_by_name(curs, client_id, service_set_name)
        service_types = selector.get_service_types_by_service_set(curs, client_id, service_set.name)
        return service_set, service_types

    def _process_service_set_row(self, curs, service_set, types_names, func):
        for n in types_names:
            try:
                t = selector.get_service_type_by_name(curs, service_set.client_id, n)
                s = ServiceSetRow(**{'service_type_id': t.id, 'service_set_id': service_set.id})
                func(curs, s)
            except EmptyResultSetError, _:
                raise ServiceTypeNotFound(n)


    @transaction()
    @authentificate
    def add_to_service_set(self, data, curs=None):
        client_id, name = data['client_id'], data['name']
        service_set, types = self._get_service_set_info(curs, client_id, name)
        types_in_set = [t.name for t in types]
        types_to_add = set(filter(lambda x: x not in types_in_set, data['service_types']))
        for n in types_to_add:
            try:
                t = selector.get_service_type_by_name(curs, service_set.client_id, n)
                r = ServiceSetRow(**{'service_type_id': t.id, 'service_set_id': service_set.id})
                mapping.insert(curs, r)
            except EmptyResultSetError, _:
                raise ServiceTypeNotFound(n)
        return response_ok()

    @transaction()
    @authentificate
    def delete_from_service_set(self, data, curs=None):
        client_id, name = data['client_id'], data['name']
        service_set, types = self._get_service_set_info(curs, client_id, name)
        types_in_set = [t.name for t in types]
        types_to_del = set(filter(lambda x: x in types_in_set, data['service_types']))
        for n in types_to_del:
            try:
                t = selector.get_service_type_by_name(curs, service_set.client_id, n)
                r = mapping.get_obj_by_fields(curs, ServiceSetRow,
                    {'service_type_id': t.id, 'service_set_id': service_set.id}, False)
                mapping.delete(curs, r)
            except EmptyResultSetError, _:
                raise ServiceTypeNotFound(n)

        return response_ok()

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
    def view_service_sets(self, data, curs=None):
        client_id = data['client_id']
        service_sets_types = self._get_service_sets_types_dict(curs, client_id)
        result = []
        for k in sorted(service_sets_types.keys()):
            result.append({'name': k, 'service_types': sorted(service_sets_types[k])})
        return response_ok(service_sets=result)

    # tariff
    @transaction()
    @authentificate
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
        tariff_id = tariffs_ids_idx[tariff_name]
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
    def modify_tariff(self, data, curs=None):
        client_id = data['client_id']
        tariff_name = data['name']
        if 'new_parent_tariff' in data:
            new_parent_name = data['new_parent_tariff']
            data['new_parent_id'] = self._get_new_parent_id(curs, client_id,
                tariff_name, new_parent_name)
            del data['new_parent_tariff']
        if 'new_service_set' in data:

            del data['new_service_set']

        loader = partial(selector.get_tariff, curs, client_id, tariff_name, for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    def delete_tariff(self, data, curs=None):
        obj = selector.get_tariff(curs, data['client_id'], data['name'])
        mapping.delete(curs, obj)
        return response_ok()

    def _get_tariffs_data(self, curs, client_id, tariffs):
        service_sets_names = selector.get_service_sets_names_indexed_by_id(curs, client_id)
        tariffs_names_idx = selector.get_tariffs_names_indexed_by_id(curs, client_id)
        parents_names_idx = selector.get_tariffs_parent_ids_indexed_by_id(curs, client_id)

        result = []
        for t in tariffs:
            ts_chain = self._calculate_tariffs_chain(t.id, tariffs_names_idx, parents_names_idx)
            _, tariffs_names = map(list, zip(*ts_chain))
            result.append(
                {
                    'name': t.name,
                    'service_set': service_sets_names.get(t.service_set_id),
                    'tariffs_chain': tariffs_names,
                    'in_archive': t.in_archive,
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
    def view_detailed_tariffs(self, data, curs=None):
        client_id = data['client_id']
        tariffs = mapping.get_list(curs, Tariff, cond=Eq('client_id', client_id))
        service_sets_types = self._get_service_sets_types_dict(curs, client_id)
        tariffs_data = self._get_tariffs_data(curs, client_id, tariffs)
        for d in tariffs_data:
            d['service_types'] = service_sets_types[d['service_set']]
        return response_ok(tariffs=tariffs_data)

    # rule
    @transaction()
    @authentificate
    def add_rule(self, data, curs=None):
        RuleChecker().check(data['rule'])
        tariff = selector.get_tariff(curs, data['client_id'], data['tariff'])
        del data['tariff']
        data['tariff_id'] = tariff.id

        service_type = selector.get_service_type_by_name(curs, data['client_id'], data['service_type'])
        del data['service_type']
        data['service_type_id'] = service_type.id

        mapping.insert(curs, Rule(**data))
        return response_ok()

    @transaction()
    @authentificate
    def modify_rule(self, data, curs=None):
        RuleChecker().check(data['new_rule'])
        loader = partial(selector.get_rule, curs, data['client_id'], data['tariff'],
            data['service_type'], True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    def delete_rule(self, data, curs=None):
        obj = selector.get_rule(curs, data['client_id'], data['tariff'], data['service_type'])
        mapping.delete(curs, obj)
        return response_ok()

    @transaction()
    @authentificate
    def get_rule(self, data, curs=None):
        client_id = data['client_id']
        tariff_name = data['tariff']
        service_type_name = data['service_type']
        rule = selector.get_rule(curs, client_id, tariff_name, service_type_name)
        return response_ok(tariff=tariff_name, service_type=service_type_name, rule=rule.rule)

    @transaction()
    @authentificate
    def view_rules(self, data, curs=None):
        client_id = data['client_id']
        tariff = selector.get_tariff(curs, client_id, data['tariff'])
        st_names_idx = selector.get_service_types_names_indexed_by_id(curs, client_id)
        rules = []
        for r in selector.get_rules(curs, client_id, tariff.name):
            rules.append({
                'service_type': st_names_idx[r.service_type_id],
                'rule': r.rule
            })
        return response_ok(tariff=tariff.name, rules=rules)

    def _get_optional_field_value(self, data, field, default=None):
        return data[field] if field in data else default,

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
                raise TariffCycleError('Tariff cycle found in chain %s' % tariffs_chain)
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

    def _find_nearest_rule(self, indexed_rules, tariffs_ids, service_type_id):
        '''
        Finds first rule implementation in tariffs listed in tariffs_ids.
        '''
        for t_id in tariffs_ids:
            k = (t_id, service_type_id)
            if k in indexed_rules:
                return indexed_rules[k]
        raise EmptyResultSetError()


    @transaction()
    @authentificate
    def get_price(self, data, curs=None):
        client_id = data['client_id']
        tariff_name = data['tariff']
        context = data['context'] if 'context' in data else {}
        service_type_name = data['service_type']

        ts_chain = self._get_tariffs_chain(curs, client_id, tariff_name)
        tariffs_ids, tariffs_names = map(list, zip(*ts_chain))

        service_type = selector.get_service_type_by_name(curs, client_id, service_type_name)
        indexed_rules = selector.get_rules_indexed_by_tariff_service_type_ids(curs, client_id,
            tariffs_ids, [service_type.id])
        try:
            rule = self._find_nearest_rule(indexed_rules, tariffs_ids, service_type.id)
        except EmptyResultSetError:
            raise RuleNotFound("Rule for service type '%s' not found in tariffs: %s" %
                (service_type_name, tariffs_names))
        response = engine.process(RequestPrice(rule, context))

        return response_ok(
            tariff=tariff_name,
            tariffs_chain=tariffs_names[:tariffs_ids.index(rule.tariff_id) + 1],
            service_type=service_type_name,
            price=response.price,
            context=context
        )

    @transaction()
    @authentificate
    def view_prices(self, data, curs=None):
        client_id = data['client_id']
        tariff_name = data['tariff']
        context = data['context'] if 'context' in data else {}

        ts_chain = self._get_tariffs_chain(curs, client_id, tariff_name)
        tariffs_ids, tariffs_names = map(list, zip(*ts_chain))

        service_sets_ids = selector.get_service_sets_ids(curs, tariffs_ids)
        service_types_ids = selector.get_service_types_ids(curs, service_sets_ids)

        indexed_rules = selector.get_rules_indexed_by_tariff_service_type_ids(curs, client_id,
            tariffs_ids, service_types_ids)

        prices = []
        service_types_names_idx = selector.get_service_types_names_indexed_by_id(curs, client_id)
        for st_id in service_types_ids:
            try:
                rule = self._find_nearest_rule(indexed_rules, tariffs_ids, st_id)
                response = engine.process(RequestPrice(rule, context))
                prices.append({
                    'tariffs_chain': self._tariffs_chain_names(rule.tariff_id, tariffs_ids, tariffs_names),
                    'service_type': service_types_names_idx[rule.service_type_id],
                    'price': response.price,
                })
            except EmptyResultSetError:
                raise RuleNotFound("Rule for service type '%s' not found in tariffs: %s" %
                    (service_types_names_idx[st_id], tariffs_names))

        return response_ok(
            tariff=tariff_name,
            context=context,
            prices=prices
        )