from helixcore.mapping.objects import Mapped


class TarificationObject(Mapped):
    __slots__ = ['id', 'environment_id', 'name']
    table = 'tarification_object'


class ServiceSet(Mapped):
    __slots__ = ['id', 'operator_id', 'name']
    table = 'service_set'


class ServiceSetRow(Mapped):
    __slots__ = ['id', 'service_type_id', 'service_set_id']
    table = 'service_set_row'


class Tariff(Mapped):
    __slots__ = ['id', 'operator_id', 'parent_id', 'service_set_id', 'name', 'in_archive']
    table = 'tariff'


class Rule(Mapped):
    __slots__ = ['id', 'operator_id', 'type', 'enabled', 'tariff_id', 'service_type_id', 'rule']
    table = 'rule'
    TYPE_DRAFT = 'draft'
    TYPE_ACTUAL = 'actual'


class ActionLog(Mapped):
    __slots__ = ['id', 'environment_id', 'session_id',
        'custom_actor_info', 'actor_user_id',
        'subject_users_ids', 'action', 'request_date',
        'remote_addr', 'request', 'response']
    table = 'action_log'
