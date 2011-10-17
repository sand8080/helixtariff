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


class Rule(Mapped):
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'

    __slots__ = ['id', 'environment_id', 'tariff_id', 'status',
        'tariffication_object_id', 'rule', 'draft_rule', 'view_order']
    table = 'rule'
