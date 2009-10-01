from functools import partial

from helixcore.mapping.actions import insert, update, delete, get_list
from helixcore.db.sql import In, Eq, Scoped, And, Insert, Delete
from helixcore.server.response import response_ok
from helixcore.server.exceptions import DataIntegrityError

from helixtariff.conf.db import transaction
from helixtariff.domain.objects import Client, ServiceType, ServiceSetDescr, ServiceSet, Tariff, Rule
from helixtariff.logic import query_builder
from helixtariff.logic import selector
from helixtariff.rulesengine.checker import RuleChecker


def mix_client_id(method):
    def decroated(self, data, curs):
        data['client_id'] = self.get_client_id(curs, data)
        method(self, data, curs)
    return decroated


class Handler(object):
    # TODO: remove me after auth integrated into protocol
    root_client_stub = 'root_client'

    '''
    Handles all API actions. Method names are called like actions.
    '''
    def ping(self, data): #IGNORE:W0613
        return response_ok()

    # TODO: implement getting client_id from data
    def get_client_id(self, curs, _):
        return selector.get_client_by_login(curs, self.root_client_stub).id

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
            update(curs, obj)

    # client
    @transaction()
    def add_client(self, data, curs=None):
        insert(curs, Client(**data))
        return response_ok()

    @transaction()
    def modify_client(self, data, curs=None):
        loader = partial(selector.get_client_by_login, curs, data['login'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    def delete_client(self, data, curs=None):
        obj = selector.get_client_by_login(curs, data['login'], for_update=True)
        delete(curs, obj)
        return response_ok()

    # server_type
    @transaction()
    @mix_client_id
    def add_service_type(self, data, curs=None):
        insert(curs, ServiceType(**data))
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
        delete(curs, t)
        return response_ok()

    # server_set_descr
    @transaction()
    def add_service_set_descr(self, data, curs=None):
        insert(curs, ServiceSetDescr(**data))
        return response_ok()

    @transaction()
    def modify_service_set_descr(self, data, curs=None):
        loader = partial(selector.get_service_set_descr_by_name, curs, data['name'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    def delete_service_set_descr(self, data, curs=None):
        t = selector.get_service_set_descr_by_name(curs, data['name'], for_update=True)
        delete(curs, t)
        return response_ok()

    # server_set
    @transaction()
    def add_to_service_set(self, data, curs=None):
        descr = selector.get_service_set_descr_by_name(curs, data['name'])
        types_names = data['types']
        types = get_list(curs, ServiceType, In('name', types_names))
        if len(types_names) != len(types):
            expected = set(types_names)
            actual = set([t.name for t in types])
            raise DataIntegrityError('Requested types not found: %s' % ', '.join(expected.difference(actual)))
        for t in types:
            s = ServiceSet(**{'service_type_id': t.id, 'service_set_descr_id': descr.id})
            insert(curs, s)
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
    def add_tariff(self, data, curs=None):
        inserts = dict(data)
        descr = selector.get_service_set_descr_by_name(curs, inserts['service_set_descr_name'])
        del inserts['service_set_descr_name']
        inserts['service_set_descr_id'] = descr.id
        query = Insert(Tariff.table, inserts)
        curs.execute(*query.glue())
        return response_ok()

    @transaction()
    def modify_tariff(self, data, curs=None):
        loader = partial(selector.get_tariff, curs, data['client_id'], data['name'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    def delete_tariff(self, data, curs=None):
        cond_client_id = Eq('client_id', data['client_id'])
        cond_name = Eq('name', data['name'])
        query = Delete(Tariff.table, And(cond_client_id, cond_name))
        curs.execute(*query.glue())
        return response_ok()

    # rule
    @transaction()
    def add_rule(self, data, curs=None):
        RuleChecker().check(data['rule'])
        tariff = selector.get_tariff(curs, data['client_id'], data['tariff_name'])
        service_type = selector.get_service_type_by_name(curs, data['service_type_name'])
        inserts = {
            'tariff_id': tariff.id,
            'service_type_id': service_type.id,
            'rule': data['rule']
        }
        query = Insert(Rule.table, inserts)
        curs.execute(*query.glue())
