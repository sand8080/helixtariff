from helixcore.mapping.objects import Mapped


class Client(Mapped):
    __slots__ = ['id', 'login', 'password']
    table = 'client'


class ServiceType(Mapped):
    __slots__ = ['id', 'client_id', 'name']
    table = 'service_type'


class ServiceSetName(Mapped):
    __slots__ = ['id', 'client_id', 'name']
    table = 'service_set_name'


class ServiceSet(Mapped):
    __slots__ = ['id', 'service_type_id', 'service_set_name_id']
    table = 'service_set'


class Tariff(Mapped):
    __slots__ = ['id', 'client_id', 'service_set_name_id', 'name', 'in_archive']
    table = 'tariff'


class Rule(Mapped):
    __slots__ = ['id', 'tariff_id', 'service_type_id', 'rule']
    table = 'rule'
