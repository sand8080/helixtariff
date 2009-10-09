from helixcore.validol.validol import Scheme, Text, Optional, Positive
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

AUTH_INFO = {
    'login': Text(),
    'password': Text(),
}

# --- client ---
ADD_CLIENT = AUTH_INFO

MODIFY_CLIENT = dict(
    {
        Optional('new_login'): Text(),
        Optional('new_password'): Text(),
    },
    **AUTH_INFO
)

DELETE_CLIENT = AUTH_INFO

# --- service type ---
SERVICE_TYPE = dict(
    {'name': Text(),},
    **AUTH_INFO
)

ADD_SERVICE_TYPE = SERVICE_TYPE

MODIFY_SERVICE_TYPE = dict(
    {
        'name': Text(),
        'new_name': Text(),
    },
    **AUTH_INFO
)

DELETE_SERVICE_TYPE = SERVICE_TYPE

GET_SERVICE_TYPES = {
    'login': Text()
}

# --- service set descr ---
ADD_SERVICE_SET_DESCR = dict(
    {'name': Text()},
    **AUTH_INFO
)

MODIFY_SERVICE_SET_DESCR = dict(
    {
        'name': Text(),
        'new_name': Text(),
    },
    **AUTH_INFO
)

DELETE_SERVICE_SET_DESCR = dict(
    {'name': Text()},
    **AUTH_INFO
)

# --- service set ---
ADD_TO_SERVICE_SET = dict(
    {
        'name': Text(),
        'types': [Text()],
    },
    **AUTH_INFO
)


DELETE_FROM_SERVICE_SET = dict(
    {
        'name': Text(),
        'types': [Text()],
    },
    **AUTH_INFO
)

DELETE_SERVICE_SET = dict(
    {'name': Text()},
    **AUTH_INFO
)

# --- tariff ---
ADD_TARIFF = dict(
    {
        'name': Text(),
        'service_set_descr_name': Text(),
        'in_archive': bool,
    },
    **AUTH_INFO
)

MODIFY_TARIFF = dict(
    {
        'name': Text(),
        Optional('new_name'): Text(),
        Optional('new_in_archive'): bool,
    },
    **AUTH_INFO
)

DELETE_TARIFF = dict(
    {'name': Text()},
    **AUTH_INFO
)

GET_TARIFF = {
    'login': Text(),
    'name': Text(),
}

GET_TARIFF_DETAILED = GET_TARIFF

# --- rule ---
ADD_RULE = dict(
    {
        'tariff_name': Text(),
        'service_type_name': Text(),
        'rule': Text(),
    },
    **AUTH_INFO
)

MODIFY_RULE = dict(
    {
        'tariff_name': Text(),
        'service_type_name': Text(),
        'new_rule': Text(),
    },
    **AUTH_INFO
)

DELETE_RULE = dict(
    {
        'tariff_name': Text(),
        'service_type_name': Text(),
    },
    **AUTH_INFO
)

# --- price ---

GET_DOMAIN_SERVICE_PRICE = {
    'login': Text(),
    'tariff_name': Text(),
    'service_type_name': Text(),
    Optional('period'): Positive(int),
    Optional('customer_id'): Text(),
}

# Useful for documentation generation
class ApiCall(object):
    def __init__(self, name, scheme, description='Not described at yet.'):
        self.name = name
        self.scheme = scheme
        self.description = description

api_scheme = [
    ApiCall('ping', Scheme(PING)),

    ApiCall('add_client', Scheme(ADD_CLIENT)),
    ApiCall('modify_client', Scheme(MODIFY_CLIENT)),
    ApiCall('delete_client', Scheme(DELETE_CLIENT)),

    ApiCall('add_service_type', Scheme(ADD_SERVICE_TYPE)),
    ApiCall('modify_service_type', Scheme(MODIFY_SERVICE_TYPE)),
    ApiCall('delete_service_type', Scheme(DELETE_SERVICE_TYPE)),
    ApiCall('get_service_types', Scheme(GET_SERVICE_TYPES)),

    ApiCall('add_service_set_descr', Scheme(ADD_SERVICE_SET_DESCR)),
    ApiCall('modify_service_set_descr', Scheme(MODIFY_SERVICE_SET_DESCR)),
    ApiCall('delete_service_set_descr', Scheme(DELETE_SERVICE_SET_DESCR)),

    ApiCall('add_to_service_set', Scheme(ADD_TO_SERVICE_SET)),
    ApiCall('delete_from_service_set', Scheme(DELETE_FROM_SERVICE_SET)),
    ApiCall('delete_service_set', Scheme(DELETE_SERVICE_SET)),

    ApiCall('add_tariff', Scheme(ADD_TARIFF)),
    ApiCall('modify_tariff', Scheme(MODIFY_TARIFF)),
    ApiCall('delete_tariff', Scheme(DELETE_TARIFF)),
    ApiCall('get_tariff', Scheme(GET_TARIFF)),
    ApiCall('get_tariff_detailed', Scheme(GET_TARIFF_DETAILED)),

    ApiCall('add_rule', Scheme(ADD_RULE)),
    ApiCall('modify_rule', Scheme(MODIFY_RULE)),
    ApiCall('delete_rule', Scheme(DELETE_RULE)),

    ApiCall('get_domain_service_price', Scheme(GET_DOMAIN_SERVICE_PRICE)),
]

action_to_scheme_map = dict((c.name, c.scheme) for c in api_scheme)

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
