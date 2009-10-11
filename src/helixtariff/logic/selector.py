from helixcore.mapping import actions
from helixcore.db.sql import Eq, Scoped, Select, In, And
from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.exceptions import DataIntegrityError

from helixtariff.domain.objects import ServiceType, ServiceSetDescr, ServiceSet, \
    Tariff, Rule, Client
from helixtariff.logic import query_builder
from helixtariff.domain import security

def get_obj_by_fields(curs, cls, fields, for_update):
    '''
    Returns object of class cls by anded conditions from fields.
    fields is dictionary of {field: value}
    '''
    and_cond = None
    for k, v in fields.items():
        eq_cond = Eq(k, v)
        if and_cond is None:
            and_cond = eq_cond
        else:
            and_cond = And(and_cond, eq_cond)
    try:
        return actions.get(curs, cls, and_cond, for_update)
    except EmptyResultSetError:
        raise DataIntegrityError('%s with %s not found in system' % (cls, fields))


def get_obj_by_field(curs, cls, field, value, for_update):
    return get_obj_by_fields(curs, cls, {field: value}, for_update)


def get_service_type_by_name(curs, client_id, name, for_update=False):
    fields = {'client_id': client_id, 'name': name}
    return get_obj_by_fields(curs, ServiceType, fields, for_update)


def get_service_set_descr_by_name(curs, name, for_update=False):
    return get_obj_by_field(curs, ServiceSetDescr, 'name', name, for_update)


def get_service_set_descr(curs, id, for_update=False): #IGNORE:W0622
    return get_obj_by_field(curs, ServiceSetDescr, 'id', id, for_update)


def get_client(curs, id, for_update=False): #IGNORE:W0622
    return get_obj_by_field(curs, Client, 'id', id, for_update)


def get_client_by_login(curs, login, for_update=False):
    return get_obj_by_field(curs, Client, 'login', login, for_update)


def get_auth_client(curs, login, password, for_update=False):
    try:
        return get_obj_by_fields(curs, Client,
            {'login': login, 'password': security.encrypt_password(password)}, for_update)
    except DataIntegrityError:
        raise security.AuthError('Access denied.')


def get_service_types_by_descr_name(curs, name, for_update=False):
    cond_descr_id = Eq('service_set_descr_id', Scoped(query_builder.select_service_set_descr_id(name)))
    sel_type_ids = Select(ServiceSet.table, columns='service_type_id', cond=cond_descr_id)
    cond_type_in = In('id', Scoped(sel_type_ids))
    return actions.get_list(curs, ServiceType, cond_type_in, order_by='id', for_update=for_update)


def get_service_types(curs, login, for_update=False):
    c = get_client_by_login(curs, login)
    return actions.get_list(curs, ServiceType, cond=Eq('client_id', c.id), for_update=for_update)


def get_tariff(curs, client_id, name, for_update=False):
    cond_id = Eq('client_id', client_id)
    cond_name = Eq('name', name)
    cond = And(cond_id, cond_name)
    return actions.get(curs, Tariff, cond=cond, for_update=for_update)


# simple request
#def get_rule(curs, client_id, tariff_name, service_type_name, for_update=False):
#    tariff = get_tariff(curs, client_id, tariff_name)
#    service_type = get_service_type_by_name(curs, client_id, service_type_name)
#
#    cond_service_type_id = Eq('service_type_id', service_type.id)
#    cond_tariff_id = Eq('tariff_id', tariff.id)
#    cond_and = And(cond_service_type_id, cond_tariff_id)
#
#    return actions.get(curs, Rule, cond=cond_and, for_update=for_update)

# complex request
def get_rule(curs, client_id, tariff_name, service_type_name, for_update=False):
    cond_client_id = Eq('client_id', client_id)
    cond_tariff_name = Eq('name', tariff_name)
    sel_tariff = Select(Tariff.table, columns='id', cond=And(cond_client_id, cond_tariff_name))

    cond_service_type_name = Eq('name', service_type_name)
    sel_service_type = Select(ServiceType.table, columns='id', cond=cond_service_type_name)

    cond_tariff_id = Eq('tariff_id', Scoped(sel_tariff))
    cond_service_type_id = Eq('service_type_id', Scoped(sel_service_type))
    return actions.get(curs, Rule, cond=And(cond_tariff_id, cond_service_type_id), for_update=for_update)
