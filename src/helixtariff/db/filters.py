from helixcore.db.sql import Eq, Like
from helixcore.db.filters import (InSessionFilter,)

from helixtariff.db.dataobject import (TarifficationObject,)
from helixcore.db.wrapper import ObjectNotFound, SelectedMoreThanOneRow
from helixtariff.error import TarifficationObjectNotFound


class TarifficationObjectFilter(InSessionFilter):
    cond_map = [
        ('id', 'id', Eq),
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
