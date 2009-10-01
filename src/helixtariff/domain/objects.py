from helixcore.mapping.objects import Mapped


class ServiceType(Mapped):
    __slots__ = ['id', 'name']
    table = 'service_type'


class ServiceSetDescr(Mapped):
    __slots__ = ['id', 'name']
    table = 'service_set_descr'


class ServiceSet(Mapped):
    __slots__ = ['id', 'service_type_id', 'service_set_descr_id']
    table = 'service_set'


class Tariff(Mapped):
    __slots__ = ['id', 'service_set_descr_id', 'client_id', 'name', 'in_archive']
    table = 'tariff'


class Rule(Mapped):
    __slots__ = ['id', 'tariff_id', 'service_type_id', 'rule']
    table = 'rule'
