from helixcore.validol.validol import Scheme, Text, Optional
from helixcore.server.errors import RequestProcessingError
import re

iso_datetime_validator = re.compile(r"""
    (\d{2,4})
    (?:-?([01]\d))?
    (?:-?([0-3]\d))?
    (?:T
        ([0-2]\d)
        (?::?([0-5]\d))?
        (?::?([0-5]\d))?
        (?:[\,\.](\d+))?
    )?
    (Z|
        ([+-][0-2]\d)
        (?::?([0-5]\d))?
    )?
    """
)

PING = {}

# --- client ---
ADD_CLIENT = {
    'login': Text(),
    'password': Text(),
}

MODIFY_CLIENT = {
    'login': Text(),
    Optional('new_login'): Text(),
    Optional('new_password'): Text(),
}

DELETE_CLIENT = {
    'login': Text(),
}

# --- service type ---
SERVICE_TYPE = {
    'name': Text(),
}

ADD_SERVICE_TYPE = SERVICE_TYPE

MODIFY_SERVICE_TYPE = {
    'name': Text(),
    'new_name': Text(),
}

DELETE_SERVICE_TYPE = SERVICE_TYPE

# --- service set descr ---
ADD_SERVICE_SET_DESCR = {
    'name': Text(),
}

MODIFY_SERVICE_SET_DESCR = {
    'name': Text(),
    'new_name': Text(),
}

DELETE_SERVICE_SET_DESCR = {
    'name': Text(),
}

# --- service set ---
ADD_TO_SERVICE_SET = {
    'name': Text(),
    'types': [Text()],
}

DELETE_FROM_SERVICE_SET = {
    'name': Text(),
    'types': [Text()],
}

DELETE_SERVICE_SET = {
    'name': Text(),
}

# --- tariff ---
ADD_TARIFF = {
    'client_id': Text(),
    'name': Text(),
    'service_set_descr_name': Text(),
    'in_archive': bool,
}

MODIFY_TARIFF = {
    'client_id': Text(),
    'name': Text(),
    Optional('new_name'): Text(),
    Optional('new_in_archive'): bool,
#    'service_set_descr_name': Text(), TODO. implement after service_set transition checker
}

DELETE_TARIFF = {
    'client_id': Text(),
    'name': Text(),
}

# --- rule ---
ADD_RULE = {
    'client_id': Text(),
    'tariff_name': Text(),
    'service_type_name': Text(),
    'rule': Text(),
}

action_to_scheme_map = {
    'ping': Scheme(PING),

    'add_client': Scheme(ADD_CLIENT),
    'modify_client': Scheme(MODIFY_CLIENT),
    'delete_client': Scheme(DELETE_CLIENT),

    'add_service_type': Scheme(ADD_SERVICE_TYPE),
    'modify_service_type': Scheme(MODIFY_SERVICE_TYPE),
    'delete_service_type': Scheme(DELETE_SERVICE_TYPE),

    'add_service_set_descr': Scheme(ADD_SERVICE_SET_DESCR),
    'modify_service_set_descr': Scheme(MODIFY_SERVICE_SET_DESCR),
    'delete_service_set_descr': Scheme(DELETE_SERVICE_SET_DESCR),

    'add_to_service_set': Scheme(ADD_TO_SERVICE_SET),
    'delete_from_service_set': Scheme(DELETE_FROM_SERVICE_SET),
    'delete_service_set': Scheme(DELETE_SERVICE_SET),

    'add_tariff': Scheme(ADD_TARIFF),
    'modify_tariff': Scheme(MODIFY_TARIFF),
    'delete_tariff': Scheme(DELETE_TARIFF),

    'add_rule': Scheme(ADD_RULE),
}

class ValidationError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Categories.validation, msg)

def validate(action_name, data):
    '''
    Validates API request data by action name
    @raise ValidationError: if validation failed for some reason
    '''
    scheme = action_to_scheme_map.get(action_name)
    if scheme is None:
        raise ValidationError('Unknown action: %s' % action_name)

    result = scheme.validate(data)
    if not result:
        raise ValidationError(
            'Validation failed for action %s. Expected scheme: %s. Actual data: %s'
            % (action_name, scheme, data)
        )
