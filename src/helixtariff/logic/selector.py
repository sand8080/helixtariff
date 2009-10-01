from helixcore.mapping import actions
from helixcore.db.sql import Eq, Scoped, Select, In, And
from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.exceptions import DataIntegrityError

from helixtariff.domain.objects import ServiceType, ServiceSetDescr, ServiceSet, \
    Tariff, Rule, Client
from helixtariff.logic import query_builder

def get_obj_by_field(curs, cls, field, value, for_update):
    try:
        return actions.get(curs, cls, Eq(field, value), for_update)
    except EmptyResultSetError:
        raise DataIntegrityError('%s with %s = %s not found in system' % (cls, field, value))

def get_service_type_by_name(curs, name, for_update=False):
    return get_obj_by_field(curs, ServiceType, 'name', name, for_update)

def get_service_set_descr_by_name(curs, name, for_update=False):
    return get_obj_by_field(curs, ServiceSetDescr, 'name', name, for_update)

def get_client_by_login(curs, login, for_update=False):
    return get_obj_by_field(curs, Client, 'login', login, for_update)

def get_service_types_by_descr_name(curs, name, for_update=False):
    cond_descr_id = Eq('service_set_descr_id', Scoped(query_builder.select_service_set_descr_id(name)))
    sel_type_ids = Select(ServiceSet.table, columns='service_type_id', cond=cond_descr_id)
    cond_type_in = In('id', Scoped(sel_type_ids))
    return actions.get_list(curs, ServiceType, cond_type_in, order_by='id', for_update=for_update)

def get_tariff(curs, client_id, name, for_update=False):
    cond_id = Eq('client_id', client_id)
    cond_name = Eq('name', name)
    cond = And(cond_id, cond_name)
    return actions.get(curs, Tariff, cond=cond, for_update=for_update)

def get_rule(curs, client_id, tariff_name, service_type_name, for_update=False):
    cond_client_id = Eq('client_id', client_id)
    cond_tariff_name = Eq('name', tariff_name)
    sel_tariff = Select(Tariff.table, columns='id', cond=And(cond_client_id, cond_tariff_name))

    cond_service_type_name = Eq('name', service_type_name)
    sel_service_type = Select(ServiceType.table, columns='id', cond=cond_service_type_name)

    cond_tariff_id = Eq('tariff_id', Scoped(sel_tariff))
    cond_service_type_id = Eq('service_type_id', Scoped(sel_service_type))
    return actions.get(curs, Rule, cond=And(cond_tariff_id, cond_service_type_id), for_update=for_update)
