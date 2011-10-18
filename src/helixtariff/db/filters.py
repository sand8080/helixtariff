from helixcore.db.sql import (Eq, Like, MoreEq, LessEq, Any, In)
from helixcore.db.filters import (InSessionFilter, EnvironmentObjectsFilter)

from helixtariff.db.dataobject import (TarifficationObject, ActionLog, Tariff,
    Rule)
from helixcore.db.wrapper import ObjectNotFound, SelectedMoreThanOneRow
from helixtariff.error import TarifficationObjectNotFound, TariffNotFound,\
    RuleNotFound


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


class RuleFilter(InSessionFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('ids', 'id', In),
        ('tariff_id', 'tariff_id', Eq),
        ('tariffication_object_id', 'tariffication_object_id', Eq),
        ('tariffication_objects_ids', 'tariffication_objects_ids', In),
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


class ActionLogFilter(EnvironmentObjectsFilter):
    cond_map = [
        ('action', 'action', Eq),
        ('session_id', 'session_id', Eq),
        ('actor_user_id', 'actor_user_id', Eq),
        ('from_request_date', 'request_date', MoreEq),
        ('to_request_date', 'request_date', LessEq),
        # OR condition
        (('subject_users_ids', 'actor_user_id'),
            ('subject_users_ids', 'actor_user_id'), (Any, Eq)),
    ]

    def __init__(self, environment_id, filter_params, paging_params, ordering_params):
        super(ActionLogFilter, self).__init__(environment_id,
            filter_params, paging_params, ordering_params, ActionLog)


