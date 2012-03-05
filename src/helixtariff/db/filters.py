from helixcore.db.sql import (Eq, Like, In, NotEq)
from helixcore.db.filters import (InSessionFilter,
    CurrencyFilter, ActionLogFilter) #@UnusedImport

from helixtariff.db.dataobject import (TarifficationObject, Tariff,
    Rule, UserTariff, TariffViewingContext)
from helixcore.db.wrapper import ObjectNotFound, SelectedMoreThanOneRow
from helixtariff.error import (TarifficationObjectNotFound, TariffNotFound,
    RuleNotFound, UserTariffNotFound, TariffViewingContextNotFound)


class TarifficationObjectFilter(InSessionFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('ids', 'id', In),
        ('name', 'name', Like),
    ]

    def __init__(self, session, filter_params, paging_params, ordering_params):
        super(TarifficationObjectFilter, self).__init__(session, filter_params,
            paging_params, ordering_params, TarifficationObject)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(TarifficationObjectFilter, self).filter_one_obj(curs,
                for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise TarifficationObjectNotFound(**self.filter_params)


class TariffFilter(InSessionFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('ids', 'id', In),
        ('name', 'name', Like),
        ('status_not_eq', 'status', NotEq),
    ]

    def __init__(self, session, filter_params, paging_params, ordering_params):
        super(TariffFilter, self).__init__(session, filter_params,
            paging_params, ordering_params, Tariff)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(TariffFilter, self).filter_one_obj(curs,
                for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise TariffNotFound(**self.filter_params)


class TariffViewingContextFilter(InSessionFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('ids', 'id', In),
        ('tariff_id', 'tariff_id', Eq),
    ]

    def __init__(self, session, filter_params, paging_params, ordering_params):
        super(TariffViewingContextFilter, self).__init__(session, filter_params,
            paging_params, ordering_params, TariffViewingContext)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(TariffViewingContextFilter, self).filter_one_obj(curs,
                for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise TariffViewingContextNotFound(**self.filter_params)


class UserTariffFilter(InSessionFilter):
    cond_map = [
        ('user_id', 'user_id', Eq),
        ('tariff_id', 'tariff_id', Eq),
        ('tariff_ids', 'tariff_id', In),
    ]

    def __init__(self, session, filter_params, paging_params, ordering_params):
        super(UserTariffFilter, self).__init__(session, filter_params,
            paging_params, ordering_params, UserTariff)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(UserTariffFilter, self).filter_one_obj(curs,
                for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise UserTariffNotFound(**self.filter_params)


class RuleFilter(InSessionFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('ids', 'id', In),
        ('tariff_id', 'tariff_id', Eq),
        ('tariff_ids', 'tariff_id', In),
        ('tariffication_object_id', 'tariffication_object_id', Eq),
        ('tariffication_object_ids', 'tariffication_object_id', In),
        ('status', 'status', Eq),
    ]

    def __init__(self, session, filter_params, paging_params, ordering_params):
        super(RuleFilter, self).__init__(session, filter_params,
            paging_params, ordering_params, Rule)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(RuleFilter, self).filter_one_obj(curs,
                for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise RuleNotFound(**self.filter_params)
