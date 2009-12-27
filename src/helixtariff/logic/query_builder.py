from helixcore.db.sql import Select, In, Eq

from helixtariff.domain.objects import ServiceType, ServiceSet

def select_service_types_ids(names):
    return Select(ServiceType.table, columns='id', cond=In('name', names))

def select_service_set_id(name):
    return Select(ServiceSet.table, columns='id', cond=Eq('name', name))