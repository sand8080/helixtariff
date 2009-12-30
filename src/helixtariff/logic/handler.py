from functools import partial

import helixcore.mapping.actions as mapping
from helixcore.db.sql import In, Eq, Scoped, And, Delete, Select
from helixcore.server.response import response_ok
from helixcore.server.exceptions import DataIntegrityError

from helixtariff.conf.db import transaction
from helixtariff.domain.objects import Client, ServiceType, \
    ServiceSet, ServiceSetRow, Tariff, Rule
from helixtariff.logic import query_builder
from helixtariff.logic import selector
from helixtariff.rulesengine.checker import RuleChecker
from helixtariff.rulesengine.engine import Engine
from helixtariff.rulesengine.interaction import RequestDomainPrice
from helixtariff.domain import security
from helixcore.db.wrapper import EmptyResultSetError
from helixtariff.error import TariffCycleError, RuleNotFound,\
    ServiceTypeNotFound


def authentificate(method):
    def decroated(self, data, curs):
        data['client_id'] = self.get_client_id(curs, data)
        del data['login']
        del data['password']
        return method(self, data, curs)
    return decroated


class Handler(object):
    '''Handles all API actions. Method names are called like actions.'''

    def ping(self, data): #IGNORE:W0613
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
    def get_service_types(self, data, curs=None):
        types = selector.get_service_types(curs, data['client_id'])
        return response_ok(
            types=[t.name for t in types]
        )

    # server_set
    @transaction()
    @authentificate
    def add_service_set(self, data, curs=None):
        mapping.insert(curs, ServiceSet(**data))
        return response_ok()

    @transaction()
    @authentificate
    def rename_service_set(self, data, curs=None):
        loader = partial(selector.get_service_set_by_name, curs, data['client_id'],
            data['name'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    def delete_service_set(self, data, curs=None):
        t = selector.get_service_set_by_name(curs, data['client_id'], data['name'], for_update=True)
        mapping.delete(curs, t)
        return response_ok()

    def _get_service_set_info(self, curs, client_id, service_set_name):
        service_set = selector.get_service_set_by_name(curs, client_id, service_set_name)
        types = selector.get_service_types_by_service_set(curs, client_id, service_set.name)
        return service_set, types

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
        types_to_add = set(filter(lambda x: x not in types_in_set, data['types']))
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
        types_to_del = set(filter(lambda x: x in types_in_set, data['types']))
        for n in types_to_del:
            try:
                t = selector.get_service_type_by_name(curs, service_set.client_id, n)
                r = mapping.get_obj_by_fields(curs, ServiceSetRow,
                    {'service_type_id': t.id, 'service_set_id': service_set.id}, False)
                mapping.delete(curs, r)
            except EmptyResultSetError, _:
                raise ServiceTypeNotFound(n)

        return response_ok()

    @transaction()
    @authentificate
    def view_service_set(self, data, curs=None):
        service_set, types = self._get_service_set_info(curs, data['client_id'], data['name'])
        return response_ok(name=service_set.name, types=sorted([t.name for t in types]))

    @transaction()
    @authentificate
    def view_service_sets(self, data, curs=None):
        client_id = data['client_id']
        service_sets = mapping.get_list(curs, ServiceSet, cond=Eq('client_id', client_id), order_by='id')
        service_sets_info = []
        for s in service_sets:
            _, types = self._get_service_set_info(curs, client_id, s.name)
            service_sets_info.append({'name': s.name, 'types': sorted([t.name for t in types])})
        return response_ok(service_sets=service_sets_info)

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

    @transaction()
    @authentificate
    def modify_tariff(self, data, curs=None):
        if 'new_parent_tariff' in data:
            parent_tariff = data['new_parent_tariff']
            if parent_tariff is None:
                parent_id = None
            else:
                parent_id = selector.get_tariff(curs, data['client_id'], parent_tariff).id
            del data['new_parent_tariff']
            data['new_parent_id'] = parent_id

        loader = partial(selector.get_tariff, curs, data['client_id'], data['name'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    def delete_tariff(self, data, curs=None):
        obj = selector.get_tariff(curs, data['client_id'], data['name'])
        mapping.delete(curs, obj)
        return response_ok()

    def _get_tariff_data(self, curs, client_id, name):
        tariff = selector.get_tariff(curs, client_id, name)
        service_set = selector.get_service_set(curs, tariff.service_set_id)
        if tariff.parent_id is None:
            pt_name = None
        else:
            pt_name = selector.get_tariff_by_id(curs, client_id, tariff.parent_id).name
        return {
            'name': tariff.name,
            'service_set': service_set.name,
            'parent_tariff': pt_name,
        }

    @transaction()
    @authentificate
    def get_tariff(self, data, curs=None):
        return response_ok(tariff=self._get_tariff_data(curs, data['client_id'], data['name']))

    @transaction()
    @authentificate
    def get_tariff_detailed(self, data, curs=None):
        client_id = data['client_id']
        tariff_data = self._get_tariff_data(curs, client_id, data['name'])
        types = selector.get_service_types_by_service_set(curs, client_id, tariff_data['service_set'])
        tariff_data['types'] = [t.name for t in types]
        return response_ok(tariff=tariff_data)

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

        del data['client_id']
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

    def _get_optional_field_value(self, data, field, default=None):
        return data[field] if field in data else default,

    # price
    def _get_tariffs_chain(self, curs, client_id, tariff_name, service_type_name):
        '''
        Finds first tariff with rule for service_type.
        If tariff with rule not found - exception raised.
        If tariff cycle found - exception raised.
        '''
        def find_next_tariff():
            tariffs_chain.append(tariff_name)
            try:
                selector.get_rule(curs, client_id, tariff_name, service_type_name)
                return None
            except EmptyResultSetError, _: #IGNORE:W0704
                pass

            if tariff_name in tariffs_set:
                raise TariffCycleError('Tariff cycle found in chain %s' % tariffs_chain)
            tariffs_set.add(tariff_name)

            tariff = selector.get_tariff(curs, client_id, tariff_name)
            if tariff.parent_id is None:
                raise RuleNotFound('No rule for service type %s in tariffs chain %s' % (service_type_name, tariffs_chain))
            return selector.get_tariff_by_id(curs, client_id, tariff.parent_id)

        tariffs_chain = []
        tariffs_set = set(tariffs_chain)

        while True:
            next_tariff = find_next_tariff()
            if next_tariff is None:
                break
            else:
                tariff_name = next_tariff.name
        return tariffs_chain

    @transaction()
    def get_domain_service_price(self, data, curs=None):
        client = selector.get_client_by_login(curs, data['login'])
        tariff_name = data['tariff']
        service_type_name = data['service_type']
        tariffs_chain = self._get_tariffs_chain(curs, client.id, tariff_name, service_type_name)
        request = RequestDomainPrice(
            client.id,
            tariffs_chain[-1],
            data['service_type'],
            period=self._get_optional_field_value(data, 'period'),
            customer_id=self._get_optional_field_value(data, 'customer_id')
        )
        response = Engine().process(request)
        result=dict(
            tariff=data['tariff'],
            tariffs_chain=tariffs_chain,
            service_type=data['service_type'],
            price=response.price
        )
        if 'customer_id' in data:
            result['customer_id'] = data['custmer_id']
        return response_ok(**result)
