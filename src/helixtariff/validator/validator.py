import re
from helixcore.server.api import ApiCall
from helixcore.validol.validol import Scheme, Text, Optional, Positive, AnyOf

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

NullableText = AnyOf(Text(), None)

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

GET_SERVICE_TYPES = AUTH_INFO

GET_SERVICE_TYPES_RESPONSE = AnyOf(
    dict(RESPONSE_STATUS_OK, types=[Text()]),
    RESPONSE_STATUS_ERROR
)

# --- service set ---
ADD_SERVICE_SET = dict(
    {'name': Text()},
    **AUTH_INFO
)

RENAME_SERVICE_SET = dict(
    {
        'name': Text(),
        'new_name': Text(),
    },
    **AUTH_INFO
)

DELETE_SERVICE_SET = dict(
    {'name': Text()},
    **AUTH_INFO
)

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

# --- tariff ---
ADD_TARIFF = dict(
    {
        'name': Text(),
        'parent_tariff': NullableText,
        'service_set': Text(),
        'in_archive': bool,
    },
    **AUTH_INFO
)

MODIFY_TARIFF = dict(
    {
        'name': Text(),
        Optional('new_name'): Text(),
        Optional('new_parent_tariff'): NullableText,
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
            'service_set': Text(),
            'parent_tariff': NullableText,
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
            'service_set': Text(),
            'parent_tariff': NullableText,
            'types': [Text()]
        }
    ),
    RESPONSE_STATUS_ERROR
)

# --- rule ---
ADD_RULE = dict(
    {
        'tariff': Text(),
        'service_type': Text(),
        'rule': Text(),
    },
    **AUTH_INFO
)

MODIFY_RULE = dict(
    {
        'tariff': Text(),
        'service_type': Text(),
        'new_rule': Text(),
    },
    **AUTH_INFO
)

DELETE_RULE = dict(
    {
        'tariff': Text(),
        'service_type': Text(),
    },
    **AUTH_INFO
)

# --- price ---

GET_DOMAIN_SERVICE_PRICE = {
    'login': Text(),
    'tariff': Text(),
    'service_type': Text(),
    Optional('period'): Positive(int),
    Optional('customer_id'): Text(),
}

GET_DOMAIN_SERVICE_PRICE_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'tariff': Text(),
            'tariffs_chain': [Text()],
            'service_type': Text(),
            'price': Text(),
            Optional('period'): Positive(int),
            Optional('customer_id'): Text(),
        }
    ),
    RESPONSE_STATUS_ERROR
)

protocol = [
    ApiCall('ping_request', Scheme(PING)),
    ApiCall('ping_response', Scheme(RESPONSE_STATUS_ONLY)),

    # client
    ApiCall('add_client_request', Scheme(ADD_CLIENT)),
    ApiCall('add_client_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('modify_client_request', Scheme(MODIFY_CLIENT)),
    ApiCall('modify_client_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('delete_client_request', Scheme(DELETE_CLIENT)),
    ApiCall('delete_client_response', Scheme(RESPONSE_STATUS_ONLY)),

    # service type
    ApiCall('add_service_type_request', Scheme(ADD_SERVICE_TYPE)),
    ApiCall('add_service_type_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('modify_service_type_request', Scheme(MODIFY_SERVICE_TYPE)),
    ApiCall('modify_service_type_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('delete_service_type_request', Scheme(DELETE_SERVICE_TYPE)),
    ApiCall('delete_service_type_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('get_service_types_request', Scheme(GET_SERVICE_TYPES)),
    ApiCall('get_service_types_response', Scheme(GET_SERVICE_TYPES_RESPONSE)),

    # service set
    ApiCall('add_service_set_request', Scheme(ADD_SERVICE_SET)),
    ApiCall('add_service_set_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('rename_service_set_request', Scheme(RENAME_SERVICE_SET)),
    ApiCall('rename_service_set_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('delete_service_set_request', Scheme(DELETE_SERVICE_SET)),
    ApiCall('delete_service_set_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('add_to_service_set_request', Scheme(ADD_TO_SERVICE_SET)),
    ApiCall('add_to_service_set_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('delete_from_service_set_request', Scheme(DELETE_FROM_SERVICE_SET)),
    ApiCall('delete_from_service_set_response', Scheme(RESPONSE_STATUS_ONLY)),

    # tariff
    ApiCall('add_tariff_request', Scheme(ADD_TARIFF)),
    ApiCall('add_tariff_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('modify_tariff_request', Scheme(MODIFY_TARIFF)),
    ApiCall('modify_tariff_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('delete_tariff_request', Scheme(DELETE_TARIFF)),
    ApiCall('delete_tariff_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('get_tariff_request', Scheme(GET_TARIFF)),
    ApiCall('get_tariff_response', Scheme(GET_TARIFF_RESPONSE)),

    ApiCall('get_tariff_detailed_request', Scheme(GET_TARIFF_DETAILED)),
    ApiCall('get_tariff_detailed_response', Scheme(GET_TARIFF_DETAILED_RESPONSE)),

    # rule
    ApiCall('add_rule_request', Scheme(ADD_RULE)),
    ApiCall('add_rule_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('modify_rule_request', Scheme(MODIFY_RULE)),
    ApiCall('modify_rule_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('delete_rule_request', Scheme(DELETE_RULE)),
    ApiCall('delete_rule_response', Scheme(RESPONSE_STATUS_ONLY)),

    # price
    ApiCall('get_domain_service_price_request', Scheme(GET_DOMAIN_SERVICE_PRICE)),
    ApiCall('get_domain_service_price_response', Scheme(GET_DOMAIN_SERVICE_PRICE_RESPONSE)),
]
