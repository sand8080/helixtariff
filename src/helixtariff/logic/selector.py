import helixcore.mapping.actions as actions
from helixcore.db.cond import Eq
from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.exceptions import DataIntegrityError

from helixtariff.domain.objects import ServiceType

def get_service_type_by_name(curs, name, for_update=False):
    try:
        return actions.get(curs, ServiceType, Eq('name', name), for_update)
    except EmptyResultSetError:
        raise DataIntegrityError('Service type with name %s not found in system' % name)

