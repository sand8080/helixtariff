import helixcore.mapping.actions as mapping
from helixcore.db.sql import Eq, Scoped, Select, In, And
from helixcore.server.exceptions import AuthError
from helixcore.db.wrapper import EmptyResultSetError

from helixtariff.domain.objects import ServiceType, \
    ServiceSet, ServiceSetRow, Tariff, Rule, Client
from helixtariff.logic import query_builder
from helixtariff.domain import security
from helixtariff.error import ClientNotFound


def get_service_type_by_name(curs, client_id, name, for_update=False):
    fields = {'client_id': client_id, 'name': name}
    return mapping.get_obj_by_fields(curs, ServiceType, fields, for_update)


def get_service_set_by_name(curs, name, for_update=False):
    return mapping.get_obj_by_field(curs, ServiceSet, 'name', name, for_update)


def get_service_set(curs, id, for_update=False): #IGNORE:W0622
    return mapping.get_obj_by_field(curs, ServiceSet, 'id', id, for_update)


def get_client(curs, id, for_update=False): #IGNORE:W0622
    try:
        return mapping.get_obj_by_field(curs, Client, 'id', id, for_update)
    except EmptyResultSetError:
        raise ClientNotFound(id)


def get_client_by_login(curs, login, for_update=False):
    try:
        return mapping.get_obj_by_field(curs, Client, 'login', login, for_update)
    except EmptyResultSetError:
        raise ClientNotFound(login)


def get_auth_client(curs, login, password, for_update=False):
    try:
        return mapping.get_obj_by_fields(curs, Client,
            {'login': login, 'password': security.encrypt_password(password)}, for_update)
    except EmptyResultSetError:
        raise AuthError('Access denied.')


def get_service_types_by_service_set_name(curs, name, for_update=False):
    cond_descr_id = Eq('service_set_id', Scoped(query_builder.select_service_set_id(name)))
    sel_type_ids = Select(ServiceSetRow.table, columns='service_type_id', cond=cond_descr_id)
    cond_type_in = In('id', Scoped(sel_type_ids))
    return mapping.get_list(curs, ServiceType, cond_type_in, order_by='id', for_update=for_update)


def get_service_types(curs, client_id, for_update=False):
    return mapping.get_list(curs, ServiceType, cond=Eq('client_id', client_id), for_update=for_update)


def get_tariff(curs, client_id, name, for_update=False):
    cond_id = Eq('client_id', client_id)
    cond_name = Eq('name', name)
    cond = And(cond_id, cond_name)
    return mapping.get(curs, Tariff, cond=cond, for_update=for_update)


def get_tariff_by_id(curs, client_id, tariff_id, for_update=False):
    cond_client_id = Eq('client_id', client_id)
    cond_id = Eq('id', tariff_id)
    cond = And(cond_client_id, cond_id)
    return mapping.get(curs, Tariff, cond=cond, for_update=for_update)


def get_rule(curs, client_id, tariff_name, service_type_name, for_update=False):
    cond_client_id = Eq('client_id', client_id)
    cond_tariff_name = Eq('name', tariff_name)
    sel_tariff = Select(Tariff.table, columns='id', cond=And(cond_client_id, cond_tariff_name))

    cond_service_type_name = Eq('name', service_type_name)
    sel_service_type = Select(ServiceType.table, columns='id', cond=cond_service_type_name)

    cond_tariff_id = Eq('tariff_id', Scoped(sel_tariff))
    cond_service_type_id = Eq('service_type_id', Scoped(sel_service_type))
    return mapping.get(curs, Rule, cond=And(cond_tariff_id, cond_service_type_id), for_update=for_update)
