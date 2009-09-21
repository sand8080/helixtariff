from helixcore.mapping import actions
from helixcore.db.sql import Eq, Select
from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.exceptions import DataIntegrityError

from helixtariff.domain.objects import ServiceType, ServiceSetDescr, ServiceSet

def get_obj_by_field(curs, cls, field, value, for_update):
    try:
        return actions.get(curs, cls, Eq(field, value), for_update)
    except EmptyResultSetError:
        raise DataIntegrityError('%s with %s = %s not found in system' % (cls, field, value))


def get_service_type_by_name(curs, name, for_update=False):
    return get_obj_by_field(curs, ServiceType, 'name', name, for_update)

def get_service_set_descr_by_name(curs, name, for_update=False):
    return get_obj_by_field(curs, ServiceSetDescr, 'name', name, for_update)

def get_service_set_by_descr_name(curs, name, for_update=False):
    pass
