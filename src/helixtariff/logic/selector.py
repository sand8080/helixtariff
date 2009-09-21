from helixcore.mapping import actions
from helixcore.db.sql import Eq, Scoped, Select, In
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

def get_service_types_by_descr_name(curs, name, for_update=False):
    sel_descr_id = Select(ServiceSetDescr.table, columns='id', cond=Eq('name', name))
    cond_descr_id = Eq('service_set_descr_id', Scoped(sel_descr_id))
    sel_type_ids = Select(ServiceSet.table, columns='service_type_id', cond=cond_descr_id)
    cond_type_in = In('id', Scoped(sel_type_ids))
    return actions.get_list(curs, ServiceType, cond_type_in, order_by='id', for_update=for_update)