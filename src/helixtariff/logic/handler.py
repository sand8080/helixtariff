from functools import partial

import helixcore.mapping.actions as mapping
from helixcore.db.sql import In, Eq, Scoped, And, Delete
from helixcore.server.response import response_ok
from helixcore.server.exceptions import DataIntegrityError

from helixtariff.conf.db import transaction
from helixtariff.domain.objects import Client, ServiceType, ServiceSetDescr, ServiceSet, Tariff, Rule
from helixtariff.logic import query_builder
from helixtariff.logic import selector
from helixtariff.rulesengine.checker import RuleChecker
from helixtariff.rulesengine.engine import Engine
from helixtariff.rulesengine.interaction import RequestDomainPrice
from helixtariff.domain import security
from helixtariff.logic.selector import get_service_set_descr


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
    def get_service_types(self, data, curs=None):
        types = selector.get_service_types(curs, data['login'])
        return response_ok(
            types=[t.name for t in types]
        )

    # server_set_descr
    @transaction()
    @authentificate
    def add_service_set_descr(self, data, curs=None):
        mapping.insert(curs, ServiceSetDescr(**data))
        return response_ok()

    @transaction()
    @authentificate
    def modify_service_set_descr(self, data, curs=None):
        loader = partial(selector.get_service_set_descr_by_name, curs, data['name'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    def delete_service_set_descr(self, data, curs=None):
        t = selector.get_service_set_descr_by_name(curs, data['name'], for_update=True)
        mapping.delete(curs, t)
        return response_ok()

    # server_set
    @transaction()
    @authentificate
    def add_to_service_set(self, data, curs=None):
        descr = selector.get_service_set_descr_by_name(curs, data['name'])
        types_names = data['types']
        types = mapping.get_list(curs, ServiceType, In('name', types_names))
        if len(types_names) != len(types):
            expected = set(types_names)
            actual = set([t.name for t in types])
            raise DataIntegrityError('Requested types not found: %s' % ', '.join(expected.difference(actual)))
        for t in types:
            s = ServiceSet(**{'service_type_id': t.id, 'service_set_descr_id': descr.id})
            mapping.insert(curs, s)
        return response_ok()

    @transaction()
    @authentificate
    def delete_from_service_set(self, data, curs=None):
        query_set_descr_id = query_builder.select_service_set_descr_id(data['name'])
        cond_set_descr_id = Eq('service_set_descr_id', Scoped(query_set_descr_id))

        query_types_ids = query_builder.select_service_types_ids(data['types'])
        cond_types_ids = In('service_type_id', Scoped(query_types_ids))

        cond_and = And(cond_set_descr_id, cond_types_ids)
        query = Delete(ServiceSet.table, cond=cond_and)
        curs.execute(*query.glue())
        return response_ok()

    @transaction()
    @authentificate
    def delete_service_set(self, data, curs=None):
        query_set_descr_id = query_builder.select_service_set_descr_id(data['name'])
        cond_set_descr_id = Eq('service_set_descr_id', Scoped(query_set_descr_id))
        query = Delete(ServiceSet.table, cond=cond_set_descr_id)
        curs.execute(*query.glue())
        return response_ok()

    # tariff
    @transaction()
    @authentificate
    def add_tariff(self, data, curs=None):
        descr = selector.get_service_set_descr_by_name(curs, data['service_set_descr_name'])
        del data['service_set_descr_name']
        data['service_set_descr_id'] = descr.id
        mapping.insert(curs, Tariff(**data))
        return response_ok()

    @transaction()
    @authentificate
    def modify_tariff(self, data, curs=None):
        loader = partial(selector.get_tariff, curs, data['client_id'], data['name'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    def delete_tariff(self, data, curs=None):
        obj = selector.get_tariff(curs, data['client_id'], data['name'])
        mapping.delete(curs, obj)
        return response_ok()

    def _get_tariff_data(self, data, curs=None):
        client = selector.get_client_by_login(curs, data['login'])
        tariff = selector.get_tariff(curs, client.id, data['name'])
        descr = get_service_set_descr(curs, tariff.service_set_descr_id)
        return {
            'name': tariff.name,
            'service_set_descr_name': descr.name,
        }

    @transaction()
    def get_tariff(self, data, curs=None):
        return response_ok(tariff=self._get_tariff_data(data, curs))

    @transaction()
    def get_tariff_detailed(self, data, curs=None):
        tariff_data = self._get_tariff_data(data, curs)
        types = selector.get_service_types_by_descr_name(curs, tariff_data['service_set_descr_name'])
        tariff_data['types'] = [t.name for t in types]
        return response_ok(tariff=tariff_data)

    # rule
    @transaction()
    @authentificate
    def add_rule(self, data, curs=None):
        RuleChecker().check(data['rule'])
        tariff = selector.get_tariff(curs, data['client_id'], data['tariff_name'])
        del data['tariff_name']
        data['tariff_id'] = tariff.id

        service_type = selector.get_service_type_by_name(curs, data['client_id'], data['service_type_name'])
        del data['service_type_name']
        data['service_type_id'] = service_type.id

        del data['client_id']
        mapping.insert(curs, Rule(**data))

    @transaction()
    @authentificate
    def modify_rule(self, data, curs=None):
        RuleChecker().check(data['new_rule'])
        loader = partial(selector.get_rule, curs, data['client_id'], data['tariff_name'],
            data['service_type_name'], True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    def delete_rule(self, data, curs=None):
        obj = selector.get_rule(curs, data['client_id'], data['tariff_name'], data['service_type_name'])
        mapping.delete(curs, obj)
        return response_ok()

    def _get_optional_field_value(self, data, field, default=None):
        return data[field] if field in data else default,

    # price
    @transaction()
    def get_domain_service_price(self, data, curs=None):
        client = selector.get_client_by_login(curs, data['login'])
        request = RequestDomainPrice(
            client.id,
            data['tariff_name'],
            data['service_type_name'],
            period=self._get_optional_field_value(data, 'period'),
            customer_id=self._get_optional_field_value(data, 'customer_id')
        )
        response = Engine().process(request)
        return response_ok(
            tariff_name=data['tariff_name'],
            service_type_name=data['service_type_name'],
            price=response.price
        )
