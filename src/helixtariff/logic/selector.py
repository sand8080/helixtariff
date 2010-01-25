import helixcore.mapping.actions as mapping
from helixcore.db.sql import Eq, Scoped, Select, In, And
from helixcore.server.exceptions import AuthError
from helixcore.db.wrapper import EmptyResultSetError, fetchall_dicts

from helixtariff.domain.objects import ServiceType, \
    ServiceSet, ServiceSetRow, Tariff, Rule, Client
from helixtariff.domain import security
from helixtariff.error import ClientNotFound, TariffNotFound, RuleNotFound,\
    ServiceTypeNotFound, ServiceSetNotFound


def get_service_type(curs, client_id, name, for_update=False):
    try:
        return mapping.get_obj_by_fields(curs, ServiceType,
            {'client_id': client_id, 'name': name}, for_update)
    except EmptyResultSetError:
        raise ServiceTypeNotFound(name)


def get_service_set_by_name(curs, client_id, name, for_update=False):
    try:
        return mapping.get_obj_by_fields(curs, ServiceSet,
            {'client_id': client_id, 'name': name}, for_update)
    except EmptyResultSetError:
        raise ServiceSetNotFound(name)


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


def get_service_types_by_service_set(curs, client_id, name, for_update=False):
    cond_name = Eq('name', name)
    cond_client_id = Eq('client_id', client_id)
    sel_ss = Select(ServiceSet.table, columns='id', cond=And(cond_name, cond_client_id))
    cond_descr_id = Eq('service_set_id', Scoped(sel_ss))
    sel_type_ids = Select(ServiceSetRow.table, columns='service_type_id', cond=cond_descr_id)
    cond_type_in = In('id', Scoped(sel_type_ids))
    return mapping.get_list(curs, ServiceType, cond_type_in, order_by='id', for_update=for_update)



def get_service_types(curs, client_id, for_update=False):
    return mapping.get_list(curs, ServiceType, cond=Eq('client_id', client_id), for_update=for_update)


def get_tariff(curs, client_id, name, for_update=False):
    cond_id = Eq('client_id', client_id)
    cond_name = Eq('name', name)
    cond = And(cond_id, cond_name)
    try:
        return mapping.get(curs, Tariff, cond=cond, for_update=for_update)
    except EmptyResultSetError:
        raise TariffNotFound(name)


def get_tariff_by_id(curs, client_id, tariff_id, for_update=False):
    cond_client_id = Eq('client_id', client_id)
    cond_id = Eq('id', tariff_id)
    cond = And(cond_client_id, cond_id)
    return mapping.get(curs, Tariff, cond=cond, for_update=for_update)


def get_child_tariffs(curs, tariff, for_update=False):
    cond_c_id = Eq('client_id', tariff.client_id)
    cond_pt_id = Eq('parent_id', tariff.id)
    return mapping.get_list(curs, Tariff, cond=And(cond_c_id, cond_pt_id), for_update=for_update)


def get_rule(curs, tariff, service_type, rule_type, for_update=False):
    try:
        cond_result = And(Eq('tariff_id', tariff.id), Eq('service_type_id', service_type.id))
        cond_result = And(cond_result, Eq('type', rule_type))
        return mapping.get(curs, Rule, cond=cond_result, for_update=for_update)
    except EmptyResultSetError:
        raise RuleNotFound("Rule not found in tariff '%s' for service_type '%s'" %
            (tariff.name, service_type.name))


def _gen_sel_service_type(name, client_id):
    cond_n = Eq('name', name)
    cond_c_id = Eq('client_id', client_id)
    return Select(ServiceType.table, columns='id', cond=And(cond_n, cond_c_id))


def get_rules(curs, tariff, rule_types, for_update=False):
    cond_c_id = Eq('client_id', tariff.client_id)
    cond_t_id = Eq('tariff_id', tariff.id)
    cond_result = And(cond_c_id, cond_t_id)
    cond_result = And(cond_result, In('type', rule_types))
    return mapping.get_list(curs, Rule, cond=cond_result, for_update=for_update)


def get_rules_for_service_types(curs, client_id, service_types_ids, for_update=False):
    cond_c_id = Eq('client_id', client_id)
    cond_st_ids = In('service_type_id', service_types_ids)
    return mapping.get_list(curs, Rule, cond=And(cond_c_id, cond_st_ids), for_update=for_update)


def get_rules_indexed_by_tariff_service_type_ids(curs, client_id, tariffs_ids, service_types_ids, for_update=False):
    '''
    @return: {(tariff_id, service_type_id, type): rule}
    '''
    cond_names = In('id', service_types_ids)
    cond_client_id = Eq('client_id', client_id)
    sel_st_id = Select(ServiceType.table, columns='id', cond=And(cond_names, cond_client_id))

    cond_st_name = In('service_type_id', Scoped(sel_st_id))
    cond_tariffs_ids = In('tariff_id', tariffs_ids)

    rules = mapping.get_list(curs, Rule, cond=And(cond_tariffs_ids, cond_st_name), for_update=for_update)
    indexed_rules = {}
    for r in rules:
        indexed_rules[(r.tariff_id, r.service_type_id, r.type)] = r
    return indexed_rules


def _get_indexed_values(curs, q, k_name, v_name):
    curs.execute(*q.glue())
    raw = fetchall_dicts(curs)
    result = {}
    for d in raw:
        result[d[k_name]] = d[v_name]
    return result


def get_service_types_names_indexed_by_id(curs, client_id, for_update=False):
    q = Select(ServiceType.table, columns=['id', 'name'], cond=Eq('client_id', client_id), for_update=for_update)
    return _get_indexed_values(curs, q, 'id', 'name')


def get_service_sets_names_indexed_by_id(curs, client_id, for_update=False):
    q = Select(ServiceSet.table, columns=['id', 'name'], cond=Eq('client_id', client_id), for_update=for_update)
    return _get_indexed_values(curs, q, 'id', 'name')


def get_service_sets_ids_by_service_type(curs, service_type, for_update=False):
    ss_rows = mapping.get_list(curs, ServiceSetRow, cond=Eq('service_type_id', service_type.id),
        for_update=for_update)
    return [r.service_set_id for r in ss_rows]


def get_tariffs_names_indexed_by_id(curs, client_id, for_update=False):
    q = Select(Tariff.table, columns=['id', 'name'], cond=Eq('client_id', client_id), for_update=for_update)
    return _get_indexed_values(curs, q, 'id', 'name')


def get_tariffs_parent_ids_indexed_by_id(curs, client_id, for_update=False):
    q = Select(Tariff.table, columns=['id', 'parent_id'], cond=Eq('client_id', client_id), for_update=for_update)
    return _get_indexed_values(curs, q, 'id', 'parent_id')


def get_tariffs_binded_with_service_sets(curs, client_id, service_sets_ids, for_update=False):
    cond_client_id = Eq('client_id', client_id)
    cond_ss_ids = In('service_set_id', service_sets_ids)
    return mapping.get_list(curs, Tariff, cond=And(cond_client_id, cond_ss_ids), for_update=for_update)


def get_service_set_rows(curs, service_sets_ids, for_update=False):
    q = Select(ServiceSetRow.table, cond=In('service_set_id', service_sets_ids), for_update=for_update)
    curs.execute(*q.glue())
    return [ServiceSetRow(**d) for d in fetchall_dicts(curs)]


def get_service_set_rows_by_service_types(curs, service_types, for_update=False):
    st_ids = [t.id for t in service_types]
    q = Select(ServiceSetRow.table, cond=In('service_set_id', st_ids), for_update=for_update)
    curs.execute(*q.glue())
    return [ServiceSetRow(**d) for d in fetchall_dicts(curs)]


def get_service_types_ids(curs, service_sets_ids, for_update=False):
    q = Select(ServiceSetRow.table, columns='service_type_id', cond=In('service_set_id', service_sets_ids),
        for_update=for_update)
    curs.execute(*q.glue())
    result = fetchall_dicts(curs)
    return [d['service_type_id'] for d in result]


def get_service_sets_ids(curs, tariffs_ids, for_update=False):
    q = Select(Tariff.table, columns='service_set_id', cond=In('id', tariffs_ids), for_update=for_update)
    curs.execute(*q.glue())
    result = fetchall_dicts(curs)
    return [d['service_set_id'] for d in result]