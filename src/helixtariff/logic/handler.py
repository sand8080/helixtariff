from helixcore.mapping.actions import insert, update, delete, get_list
from helixcore.db.sql import In, Eq, Delete, Scoped, And
#from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.response import response_ok
from helixcore.server.exceptions import DataIntegrityError

#from helixcore.server.exceptions import ActionNotAllowedError, DataIntegrityError

from helixtariff.conf.db import transaction
from helixtariff.domain.objects import ServiceType, ServiceSetDescr, ServiceSet
from helixtariff.logic import query_builder
from helixtariff.logic import selector

class Handler(object):
    '''
    Handles all API actions. Method names are called like actions.
    '''
    def ping(self, data): #IGNORE:W0613
        return response_ok()

    # server_type
    @transaction()
    def add_service_type(self, data, curs=None):
        insert(curs, ServiceType(**data))
        return response_ok()

    @transaction()
    def modify_service_type(self, data, curs=None):
        t = selector.get_service_type_by_name(curs, data['name'], True)
        t.name = data['new_name']
        update(curs, t)
        return response_ok()

    @transaction()
    def delete_service_type(self, data, curs=None):
        t = selector.get_service_type_by_name(curs, data['name'], True)
        delete(curs, t)
        return response_ok()

    # server_set_descr
    @transaction()
    def add_service_set_descr(self, data, curs=None):
        insert(curs, ServiceSetDescr(**data))
        return response_ok()

    @transaction()
    def modify_service_set_descr(self, data, curs=None):
        t = selector.get_service_set_descr_by_name(curs, data['name'], True)
        t.name = data['new_name']
        update(curs, t)
        return response_ok()

    @transaction()
    def delete_service_set_descr(self, data, curs=None):
        t = selector.get_service_set_descr_by_name(curs, data['name'], True)
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
