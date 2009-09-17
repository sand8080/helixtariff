from helixcore.validol.validol import Scheme, Text
from helixcore.server.errors import RequestProcessingError
import re

#amount_validator = (NonNegative(int), NonNegative(int))
#nonnegative_amount_validator = (Positive(int), NonNegative(int))
#locking_order_validator = AnyOf(None, [AnyOf('available_real_amount', 'available_virtual_amount')])

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

PING = {
}

# --- service type ---
ADD_SERVICE_TYPE = {
    'name': Text(),
}

MODIFY_SERVICE_TYPE = {
    'name': Text(),
    'new_name': Text(),
}

DELETE_SERVICE_TYPE = {
    'name': Text(),
}

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


action_to_scheme_map = {
    'ping': Scheme(PING),
    'add_service_type': Scheme(ADD_SERVICE_TYPE),
    'modify_service_type': Scheme(MODIFY_SERVICE_TYPE),
    'delete_service_type': Scheme(DELETE_SERVICE_TYPE),
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
