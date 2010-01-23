from helixcore.mapping.objects import Mapped


class Client(Mapped):
    __slots__ = ['id', 'login', 'password']
    table = 'client'


class ServiceType(Mapped):
    __slots__ = ['id', 'client_id', 'name']
    table = 'service_type'


class ServiceSet(Mapped):
    __slots__ = ['id', 'client_id', 'name']
    table = 'service_set'


class ServiceSetRow(Mapped):
    __slots__ = ['id', 'service_type_id', 'service_set_id']
    table = 'service_set_row'


class Tariff(Mapped):
    __slots__ = ['id', 'client_id', 'parent_id', 'service_set_id', 'name', 'in_archive']
    table = 'tariff'


class Rule(Mapped):
    __slots__ = ['id', 'client_id', 'type', 'enabled', 'tariff_id', 'service_type_id', 'rule']
    table = 'rule'
    TYPE_DRAFT = 'draft'
    TYPE_ACTUAL = 'actual'

