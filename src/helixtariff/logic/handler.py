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
from helixtariff.domain import security


def mix_client_id(method):
    def decroated(self, data, curs):
        data['client_id'] = self.get_client_id(curs, data)
        method(self, data, curs)
    return decroated

def authentificate(method):
    def decroated(self, data, curs):
        data['client_id'] = self.get_client_id(curs, data)
        del data['login']
        del data['password']
        method(self, data, curs)
    return decroated


class Handler(object):
    '''Handles all API actions. Method names are called like actions.'''

    # TODO: remove me after auth integrated into protocol
    root_client_stub = 'root_client'

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
    @mix_client_id
    def add_service_type(self, data, curs=None):
        mapping.insert(curs, ServiceType(**data))
        return response_ok()

    @transaction()
    @mix_client_id
    def modify_service_type(self, data, curs=None):
        loader = partial(selector.get_service_type_by_name, curs, data['client_id'], data['name'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @mix_client_id
    def delete_service_type(self, data, curs=None):
        t = selector.get_service_type_by_name(curs, data['client_id'], data['name'], for_update=True)
        mapping.delete(curs, t)
        return response_ok()

    # server_set_descr
    @transaction()
    @mix_client_id
    def add_service_set_descr(self, data, curs=None):
        mapping.insert(curs, ServiceSetDescr(**data))
        return response_ok()

    @transaction()
    @mix_client_id
    def modify_service_set_descr(self, data, curs=None):
        loader = partial(selector.get_service_set_descr_by_name, curs, data['name'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @mix_client_id
    def delete_service_set_descr(self, data, curs=None):
        t = selector.get_service_set_descr_by_name(curs, data['name'], for_update=True)
        mapping.delete(curs, t)
        return response_ok()

    # server_set
    @transaction()
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
    def delete_service_set(self, data, curs=None):
        query_set_descr_id = query_builder.select_service_set_descr_id(data['name'])
        cond_set_descr_id = Eq('service_set_descr_id', Scoped(query_set_descr_id))
        query = Delete(ServiceSet.table, cond=cond_set_descr_id)
        curs.execute(*query.glue())
        return response_ok()

    # tariff
    @transaction()
    @mix_client_id
    def add_tariff(self, data, curs=None):
        descr = selector.get_service_set_descr_by_name(curs, data['service_set_descr_name'])
        del data['service_set_descr_name']
        data['service_set_descr_id'] = descr.id
        mapping.insert(curs, Tariff(**data))
        return response_ok()

    @transaction()
    @mix_client_id
    def modify_tariff(self, data, curs=None):
        loader = partial(selector.get_tariff, curs, data['client_id'], data['name'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @mix_client_id
    def delete_tariff(self, data, curs=None):
        obj = selector.get_tariff(curs, data['client_id'], data['name'])
        mapping.delete(curs, obj)
        return response_ok()

    # rule
    @transaction()
    @mix_client_id
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
    @mix_client_id
    def modify_rule(self, data, curs=None):
        RuleChecker().check(data['new_rule'])
        loader = partial(selector.get_rule, curs, data['client_id'], data['tariff_name'],
            data['service_type_name'], True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @mix_client_id
    def delete_rule(self, data, curs=None):
        obj = selector.get_rule(curs, data['client_id'], data['tariff_name'], data['service_type_name'])
        mapping.delete(curs, obj)
        return response_ok()
