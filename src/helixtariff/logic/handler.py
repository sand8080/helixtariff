from helixcore.mapping.actions import insert, update, delete
#from helixcore.db.wrapper import EmptyResultSetError
#from helixcore.db.cond import Eq, And
from helixcore.server.response import response_ok
#from helixcore.server.exceptions import ActionNotAllowedError, DataIntegrityError

from helixtariff.conf.db import transaction
from helixtariff.domain.objects import ServiceType
from helixtariff.logic.selector import get_service_type_by_name

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
        t = get_service_type_by_name(curs, data['name'], True)
        t.name = data['new_name']
        update(curs, t)
        return response_ok()

    @transaction()
    def delete_service_type(self, data, curs=None):
        t = get_service_type_by_name(curs, data['name'], True)
        delete(curs, t)
        return response_ok()
