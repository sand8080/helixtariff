from helixcore.mapping.objects import Mapped


class TarifficationObject(Mapped):
    __slots__ = ['id', 'environment_id', 'name']
    table = 'tariffication_object'


class Tariff(Mapped):
    TYPE_PUBLIC = 'public'
    TYPE_PERSONAL = 'personal'

    STATUS_ACTIVE = 'active'
    STATUS_ARCHIVE = 'archive'
    STATUS_INACTIVE = 'inactive'

    __slots__ = ['id', 'environment_id', 'name', 'parent_tariff_id',
        'type', 'status']
    table = 'tariff'


class ActionLog(Mapped):
    __slots__ = ['id', 'environment_id', 'session_id',
        'custom_actor_info', 'actor_user_id',
        'subject_users_ids', 'action', 'request_date',
        'remote_addr', 'request', 'response']
    table = 'action_log'


#class ServiceSet(Mapped):
#    __slots__ = ['id', 'operator_id', 'name']
#    table = 'service_set'
#
#
#class ServiceSetRow(Mapped):
#    __slots__ = ['id', 'service_type_id', 'service_set_id']
#    table = 'service_set_row'
#
#
#
#class Rule(Mapped):
#    __slots__ = ['id', 'operator_id', 'type', 'enabled', 'tariff_id', 'service_type_id', 'rule']
#    table = 'rule'
#    TYPE_DRAFT = 'draft'
#    TYPE_ACTUAL = 'actual'


