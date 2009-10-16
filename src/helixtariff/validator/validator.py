from helixcore.validol.validol import Scheme, Text, Optional, Positive, AnyOf
from helixcore.server.errors import RequestProcessingError
from helixcore.validol.docsgenerator import DocItem
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

RESPONSE_STATUS_OK = {'status': 'ok'}

RESPONSE_STATUS_ERROR = {
    'status': 'error',
    'category': Text(),
    'message': Text(),
}

RESPONSE_STATUS_ONLY = AnyOf(RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR)

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

GET_SERVICE_TYPES_RESPONSE = AnyOf(
    dict(RESPONSE_STATUS_OK, types=[Text()]),
    RESPONSE_STATUS_ERROR
)

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

GET_TARIFF_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        tariff={
            'name': Text(),
            'service_set_descr_name': Text()
        }
    ),
    RESPONSE_STATUS_ERROR
)

GET_TARIFF_DETAILED = GET_TARIFF

GET_TARIFF_DETAILED_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        tariff={
            'name': Text(),
            'service_set_descr_name': Text(),
            'types': [Text()]
        }
    ),
    RESPONSE_STATUS_ERROR
)

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

GET_DOMAIN_SERVICE_PRICE_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'tariff_name': Text(),
            'service_type_name': Text(),
            'price': Text(),
            Optional('period'): Positive(int),
            Optional('customer_id'): Text(),
        }
    ),
    RESPONSE_STATUS_ERROR
)

protocol = [
    DocItem('ping_request', Scheme(PING)),
    DocItem('ping_response', Scheme(RESPONSE_STATUS_ONLY)),

    # client
    DocItem('add_client_request', Scheme(ADD_CLIENT)),
    DocItem('add_client_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('modify_client_request', Scheme(MODIFY_CLIENT)),
    DocItem('modify_client_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('delete_client_request', Scheme(DELETE_CLIENT)),
    DocItem('delete_client_response', Scheme(RESPONSE_STATUS_ONLY)),

    # service type
    DocItem('add_service_type_request', Scheme(ADD_SERVICE_TYPE)),
    DocItem('add_service_type_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('modify_service_type_request', Scheme(MODIFY_SERVICE_TYPE)),
    DocItem('modify_service_type_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('delete_service_type_request', Scheme(DELETE_SERVICE_TYPE)),
    DocItem('delete_service_type_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('get_service_types_request', Scheme(GET_SERVICE_TYPES)),
    DocItem('get_service_types_response', Scheme(GET_SERVICE_TYPES_RESPONSE)),

    # service set description
    DocItem('add_service_set_descr_request', Scheme(ADD_SERVICE_SET_DESCR)),
    DocItem('add_service_set_descr_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('modify_service_set_descr_request', Scheme(MODIFY_SERVICE_SET_DESCR)),
    DocItem('modify_service_set_descr_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('delete_service_set_descr_request', Scheme(DELETE_SERVICE_SET_DESCR)),
    DocItem('delete_service_set_descr_response', Scheme(RESPONSE_STATUS_ONLY)),

    # service set
    DocItem('add_to_service_set_request', Scheme(ADD_TO_SERVICE_SET)),
    DocItem('add_to_service_set_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('delete_from_service_set_request', Scheme(DELETE_FROM_SERVICE_SET)),
    DocItem('delete_from_service_set_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('delete_service_set_request', Scheme(DELETE_SERVICE_SET)),
    DocItem('delete_service_set_response', Scheme(RESPONSE_STATUS_ONLY)),

    # tariff
    DocItem('add_tariff_request', Scheme(ADD_TARIFF)),
    DocItem('add_tariff_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('modify_tariff_request', Scheme(MODIFY_TARIFF)),
    DocItem('modify_tariff_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('delete_tariff_request', Scheme(DELETE_TARIFF)),
    DocItem('delete_tariff_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('get_tariff_request', Scheme(GET_TARIFF)),
    DocItem('get_tariff_response', Scheme(GET_TARIFF_RESPONSE)),

    DocItem('get_tariff_detailed_request', Scheme(GET_TARIFF_DETAILED)),
    DocItem('get_tariff_detailed_response', Scheme(GET_TARIFF_DETAILED_RESPONSE)),

    # rule
    DocItem('add_rule_request', Scheme(ADD_RULE)),
    DocItem('add_rule_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('modify_rule_request', Scheme(MODIFY_RULE)),
    DocItem('modify_rule_response', Scheme(RESPONSE_STATUS_ONLY)),

    DocItem('delete_rule_request', Scheme(DELETE_RULE)),
    DocItem('delete_rule_response', Scheme(RESPONSE_STATUS_ONLY)),

    # price
    DocItem('get_domain_service_price_request', Scheme(GET_DOMAIN_SERVICE_PRICE)),
    DocItem('get_domain_service_price_response', Scheme(GET_DOMAIN_SERVICE_PRICE_RESPONSE)),
]

action_to_scheme_map = dict((c.name, c.scheme) for c in protocol)


class ValidationError(RequestProcessingError):
    def __init__(self, msg):
        RequestProcessingError.__init__(self, RequestProcessingError.Categories.validation, msg)


def _validate(call_name, data):
    scheme = action_to_scheme_map.get(call_name)
    if scheme is None:
        raise ValidationError('Scheme for %s not found' % call_name)

    result = scheme.validate(data)
    if not result:
        raise ValidationError(
            'Validation failed for action %s. Expected scheme: %s. Actual data: %s'
            % (call_name, scheme, data)
        )


def validate_request(action_name, data):
    '''
    Validates API request data by action name
    @raise ValidationError: if validation failed for some reason
    '''
    return _validate('%s_request' % action_name, data)


def validate_response(action_name, data):
    '''
    Validates API response data by action name
    @raise ValidationError: if validation failed for some reason
    '''
    return _validate('%s_response' % action_name, data)
