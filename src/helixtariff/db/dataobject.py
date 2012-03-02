from helixcore.mapping.objects import Mapped, serialize_field
from helixcore.db.dataobject import Currency, ActionLog #@UnusedImport


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
        'type', 'status', 'currency_id']
    table = 'tariff'


class Rule(Mapped):
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'

    __slots__ = ['id', 'environment_id', 'tariff_id', 'status',
        'tariffication_object_id', 'rule', 'draft_rule', 'view_order']
    table = 'rule'


class UserTariff(Mapped):
    __slots__ = ['id', 'environment_id', 'user_id', 'tariff_id']
    table = 'user_tariff'


class TariffViewingContext(Mapped):
    __slots__ = ['id', 'environment_id', 'tariff_id', 'name', 'view_order',
        'serialized_context']
    table = 'tariff_viewing_context'

    def __init__(self, **kwargs):
        d = serialize_field(kwargs, 'context', 'serialized_context')
        super(TariffViewingContext, self).__init__(**d)
