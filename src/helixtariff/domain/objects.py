from helixcore.mapping.objects import Mapped


class Client(Mapped):
    __slots__ = ['id', 'login', 'password']
    table = 'client'

    def __repr__(self, except_attrs=()):
        return super(Client, self).__repr__(except_attrs=except_attrs + ('password',))

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


class ActionLog(Mapped):
    __slots__ = ['id', 'client_id', 'source', 'action', 'request_date', 'request', 'response']
    table = 'action_log'
