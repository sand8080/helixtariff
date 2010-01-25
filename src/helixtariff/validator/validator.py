from helixcore.server.api import ApiCall
from helixcore.validol.validol import Scheme, Text, Optional, FlatDict, AnyOf, DecimalText
from helixtariff.domain.objects import Rule


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

VIEW_SERVICE_TYPES = AUTH_INFO

VIEW_SERVICE_TYPES_RESPONSE = AnyOf(
    dict(RESPONSE_STATUS_OK, service_types=[Text()]),
    RESPONSE_STATUS_ERROR
)

VIEW_SERVICE_TYPES_DETAILED = VIEW_SERVICE_TYPES

VIEW_SERVICE_TYPES_DETAILED_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        service_types=[
            {'name': Text(), 'service_sets': [Text()]}
        ]
    ),
    RESPONSE_STATUS_ERROR
)

# --- service set ---
ADD_SERVICE_SET = dict(
    {
        'name': Text(),
        'service_types': [Text()],
    },
    **AUTH_INFO
)

MODIFY_SERVICE_SET = dict(
    {
        'name': Text(),
        Optional('new_name'): Text(),
        Optional('new_service_types'): [Text()],
    },
    **AUTH_INFO
)

DELETE_SERVICE_SET = dict(
    {'name': Text()},
    **AUTH_INFO
)

SERVICE_SET_INFO = dict({
    'name': Text(),
    'service_types': [Text()],
})

GET_SERVICE_SET = dict(
    {'name': Text()},
    **AUTH_INFO
)

GET_SERVICE_SET_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **SERVICE_SET_INFO
    ),
    RESPONSE_STATUS_ERROR
)

VIEW_SERVICE_SETS = AUTH_INFO

VIEW_SERVICE_SETS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'service_sets': [SERVICE_SET_INFO]}
    ),
    RESPONSE_STATUS_ERROR
)

GET_SERVICE_SET_DETAILED = GET_SERVICE_SET
SERVICE_SET_INFO_DETAILED = dict({'tariffs': [Text()]}, **SERVICE_SET_INFO)

GET_SERVICE_SET_DETAILED_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **SERVICE_SET_INFO_DETAILED
    ),
    RESPONSE_STATUS_ERROR
)

VIEW_SERVICE_SETS_DETAILED = VIEW_SERVICE_SETS

VIEW_SERVICE_SETS_DETAILED_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'service_sets': [SERVICE_SET_INFO_DETAILED]}
    ),
    RESPONSE_STATUS_ERROR
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
        Optional('new_service_set'): Text(),
    },
    **AUTH_INFO
)

DELETE_TARIFF = dict(
    {'name': Text()},
    **AUTH_INFO
)

TARIFF_INFO = {
    'name': Text(),
    'service_set': Text(),
    'tariffs_chain': [Text()],
    'in_archive': bool,
}

GET_TARIFF = dict(
    {'name': Text()},
    **AUTH_INFO
)

GET_TARIFF_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **TARIFF_INFO
    ),
    RESPONSE_STATUS_ERROR
)

GET_TARIFF_DETAILED = GET_TARIFF

DETAILED_TARIFF_INFO = dict(
    {'service_types': [Text()]},
    **TARIFF_INFO
)

GET_TARIFF_DETAILED_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **DETAILED_TARIFF_INFO
    ),
    RESPONSE_STATUS_ERROR
)

VIEW_TARIFFS = AUTH_INFO

VIEW_TARIFFS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'tariffs': [TARIFF_INFO]}
    ),
    RESPONSE_STATUS_ERROR
)

VIEW_DETAILED_TARIFFS = VIEW_TARIFFS
VIEW_DETAILED_TARIFFS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'tariffs': [DETAILED_TARIFF_INFO]}
    ),
    RESPONSE_STATUS_ERROR
)


# --- rule ---
SAVE_DRAFT_RULE = dict(
    {
        'tariff': Text(),
        'service_type': Text(),
        'rule': Text(),
        'enabled': bool,
    },
    **AUTH_INFO
)

MAKE_DRAFT_RULES_ACTUAL = dict(
    {'tariff': Text()},
    **AUTH_INFO
)

MODIFY_ACTUAL_RULE = dict(
    {
        'tariff': Text(),
        'service_type': Text(),
        'new_enabled': bool,
    },
    **AUTH_INFO
)

RULE_TYPES = AnyOf(Rule.TYPE_ACTUAL, Rule.TYPE_DRAFT)

GET_RULE = dict(
    {
        'tariff': Text(),
        'service_type': Text(),
        'type': RULE_TYPES
    },
    **AUTH_INFO
)

RULE_INFO = {
    'service_type': Text(),
    'rule': Text(),
    'type': RULE_TYPES,
    'enabled': bool,
}

GET_RULE_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **dict({'tariff': Text()}, **RULE_INFO)
    ),
    RESPONSE_STATUS_ERROR
)

VIEW_RULES = dict(
    {'tariff': Text()},
    **AUTH_INFO
)

VIEW_RULES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'tariff': Text(),
            'rules': [RULE_INFO],
        }
    ),
    RESPONSE_STATUS_ERROR
)


# --- price ---
GET_PRICE = dict(
    {
        'tariff': Text(),
        'service_type': Text(),
        Optional('context'): FlatDict(),
    },
    **AUTH_INFO
)

PRICE_CALC_NORMAL = 'normal'
PRICE_CALC_SERVICE_TYPE_DISABLED = 'service_type_disabled'
PRICE_CALC_PRICE_UNDEFINED = 'price_undefined'
PRICE_CALC_RULE_DISABLED = 'rule_disabled'
PRICE_CALCULATION = AnyOf(
    PRICE_CALC_NORMAL,
    PRICE_CALC_SERVICE_TYPE_DISABLED,
    PRICE_CALC_PRICE_UNDEFINED,
    PRICE_CALC_RULE_DISABLED,
)

PRICE_INFO= {
    'service_type': Text(),
    'tariffs_chain': [Text()],
    'price': AnyOf(DecimalText(), None),
    'price_calculation': PRICE_CALCULATION,
    'draft_tariffs_chain': [Text()],
    'draft_price': AnyOf(DecimalText(), None),
    'draft_price_calculation': PRICE_CALCULATION,
}

GET_PRICE_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **dict(
            {
                'tariff': Text(),
                'context': FlatDict(),
            },
            **PRICE_INFO
        )
    ),
    RESPONSE_STATUS_ERROR
)

VIEW_PRICES = dict(
    {
        'tariff': Text(),
        Optional('context'): FlatDict(),
    },
    **AUTH_INFO
)

VIEW_PRICES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'tariff': Text(),
            'context': FlatDict(),
            'prices': [PRICE_INFO],
        }
    ),
    RESPONSE_STATUS_ERROR
)


# -- protocol --
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

    ApiCall('view_service_types_request', Scheme(VIEW_SERVICE_TYPES)),
    ApiCall('view_service_types_response', Scheme(VIEW_SERVICE_TYPES_RESPONSE)),

    ApiCall('view_service_types_detailed_request', Scheme(VIEW_SERVICE_TYPES_DETAILED)),
    ApiCall('view_service_types_detailed_response', Scheme(VIEW_SERVICE_TYPES_DETAILED_RESPONSE)),

    # service set
    ApiCall('add_service_set_request', Scheme(ADD_SERVICE_SET)),
    ApiCall('add_service_set_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('modify_service_set_request', Scheme(MODIFY_SERVICE_SET)),
    ApiCall('modify_service_set_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('delete_service_set_request', Scheme(DELETE_SERVICE_SET)),
    ApiCall('delete_service_set_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('get_service_set_request', Scheme(GET_SERVICE_SET)),
    ApiCall('get_service_set_response', Scheme(GET_SERVICE_SET_RESPONSE)),

    ApiCall('get_service_set_detailed_request', Scheme(GET_SERVICE_SET_DETAILED)),
    ApiCall('get_service_set_detailed_response', Scheme(GET_SERVICE_SET_DETAILED_RESPONSE)),

    ApiCall('view_service_sets_request', Scheme(VIEW_SERVICE_SETS)),
    ApiCall('view_service_sets_response', Scheme(VIEW_SERVICE_SETS_RESPONSE)),

    ApiCall('view_service_sets_detailed_request', Scheme(VIEW_SERVICE_SETS_DETAILED)),
    ApiCall('view_service_sets_detailed_response', Scheme(VIEW_SERVICE_SETS_DETAILED_RESPONSE)),

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

    ApiCall('view_tariffs_request', Scheme(VIEW_TARIFFS)),
    ApiCall('view_tariffs_response', Scheme(VIEW_TARIFFS_RESPONSE)),

    ApiCall('view_detailed_tariffs_request', Scheme(VIEW_DETAILED_TARIFFS)),
    ApiCall('view_detailed_tariffs_response', Scheme(VIEW_DETAILED_TARIFFS_RESPONSE)),

    # rule
    ApiCall('save_draft_rule_request', Scheme(SAVE_DRAFT_RULE)),
    ApiCall('save_draft_rule_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('make_draft_rules_actual_request', Scheme(MAKE_DRAFT_RULES_ACTUAL)),
    ApiCall('make_draft_rules_actual_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('modify_actual_rule_request', Scheme(MODIFY_ACTUAL_RULE)),
    ApiCall('modify_actual_rule_response', Scheme(RESPONSE_STATUS_ONLY)),

    ApiCall('get_rule_request', Scheme(GET_RULE)),
    ApiCall('get_rule_response', Scheme(GET_RULE_RESPONSE)),

    ApiCall('view_rules_request', Scheme(VIEW_RULES)),
    ApiCall('view_rules_response', Scheme(VIEW_RULES_RESPONSE)),

    # price
    ApiCall('get_price_request', Scheme(GET_PRICE)),
    ApiCall('get_price_response', Scheme(GET_PRICE_RESPONSE)),

    ApiCall('view_prices_request', Scheme(VIEW_PRICES)),
    ApiCall('view_prices_response', Scheme(VIEW_PRICES_RESPONSE)),

]
