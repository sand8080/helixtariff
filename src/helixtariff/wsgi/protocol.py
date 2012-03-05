from helixcore.server.api import ApiCall
from helixcore.json_validator import (Scheme, TEXT, Optional, AnyOf,
    NON_NEGATIVE_INT, NULLABLE_TEXT, DECIMAL_TEXT, NULLABLE_INT, POSITIVE_INT,
    ID, INT)
from helixcore.server.protocol_primitives import (PING_REQUEST, PING_RESPONSE,
    LOGIN_REQUEST, LOGIN_RESPONSE, LOGOUT_REQUEST, LOGOUT_RESPONSE,
    AUTHORIZED_REQUEST_AUTH_INFO, ADDING_OBJECT_RESPONSE, RESPONSE_STATUS_ONLY,
    GET_ACTION_LOGS_REQUEST, GET_ACTION_LOGS_RESPONSE,
    GET_ACTION_LOGS_SELF_REQUEST, GET_ACTION_LOGS_SELF_RESPONSE,
    REQUEST_PAGING_PARAMS, RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR)


TARIFF_TYPE_VALIDATOR = AnyOf('public', 'personal')
TARIFF_STATUS_VALIDATOR = AnyOf('active', 'archive', 'inactive')
RULE_STATUS_VALIDATOR = AnyOf('active', 'inactive')


ADD_TARIFFICATION_OBJECT_REQUEST = dict(
    {'name': TEXT},
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_TARIFFICATION_OBJECT_RESPONSE = ADDING_OBJECT_RESPONSE

GET_TARIFFICATION_OBJECTS_REQUEST = dict(
    {
        'filter_params': {
            Optional('id'): int,
            Optional('ids'): [int],
            Optional('name'): TEXT,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

TARIFFICATION_OBJECT_INFO = {
    'id': int,
    'name': TEXT,
}

GET_TARIFFICATION_OBJECTS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'tariffication_objects': [TARIFFICATION_OBJECT_INFO],
            'total': NON_NEGATIVE_INT,
        }
    ),
    RESPONSE_STATUS_ERROR
)

MODIFY_TARIFFICATION_OBJECT_REQUEST = dict(
    {
        'id': int,
        'new_name': TEXT,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_TARIFFICATION_OBJECT_RESPONSE = RESPONSE_STATUS_ONLY

DELETE_TARIFFICATION_OBJECT_REQUEST = dict(
    {'id': int},
    **AUTHORIZED_REQUEST_AUTH_INFO
)

DELETE_TARIFFICATION_OBJECT_RESPONSE = RESPONSE_STATUS_ONLY

ADD_TARIFF_REQUEST = dict(
    {
        'name': TEXT,
        'parent_tariff_id': NULLABLE_INT,
        Optional('currency'): NULLABLE_TEXT,
        'type': AnyOf('public', 'personal'),
        'status': AnyOf('active', 'archive', 'inactive'),
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_TARIFF_RESPONSE = ADDING_OBJECT_RESPONSE

GET_TARIFFS_REQUEST = dict(
    {
        'filter_params': {
            Optional('id'): int,
            Optional('ids'): [int],
            Optional('name'): TEXT,
            Optional('type'): TARIFF_TYPE_VALIDATOR,
            Optional('status'): TARIFF_STATUS_VALIDATOR,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id', 'name', '-name')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

TARIFF_INFO = {
    'id': int,
    'name': TEXT,
    'parent_tariffs': [{'id': int, 'name': TEXT, 'status': TARIFF_STATUS_VALIDATOR, 'currency': NULLABLE_TEXT}],
    'type': TARIFF_TYPE_VALIDATOR,
    'status': TARIFF_STATUS_VALIDATOR,
    'currency': NULLABLE_TEXT,
}

GET_TARIFFS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'tariffs': [TARIFF_INFO],
            'total': NON_NEGATIVE_INT,
        }
    ),
    RESPONSE_STATUS_ERROR
)

MODIFY_TARIFF_REQUEST = dict(
    {
        'id': int,
        Optional('new_name'): TEXT,
        Optional('new_parent_tariff_id'): NULLABLE_INT,
        Optional('new_type'): TARIFF_TYPE_VALIDATOR,
        Optional('new_currency'): NULLABLE_TEXT,
        Optional('new_status'): TARIFF_STATUS_VALIDATOR,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_TARIFF_RESPONSE = RESPONSE_STATUS_ONLY

DELETE_TARIFF_REQUEST = dict(
    {'id': int},
    **AUTHORIZED_REQUEST_AUTH_INFO
)

DELETE_TARIFF_RESPONSE = RESPONSE_STATUS_ONLY

VIEW_TARIFF_CONTEXT_PARAM = AnyOf(
    {'name': TEXT, 'value': TEXT},
    {'name': TEXT, 'value': INT},
    {'name': TEXT, 'value': TEXT},
)

ADD_TARIFF_VIEWING_CONTEXT_REQUEST = dict(
    {
        'tariff_id': ID,
        'name': NULLABLE_TEXT,
        'view_order': NON_NEGATIVE_INT,
        'context': [VIEW_TARIFF_CONTEXT_PARAM],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_TARIFF_VIEWING_CONTEXT_RESPONSE = ADDING_OBJECT_RESPONSE

GET_TARIFF_VIEWING_CONTEXTS_REQUEST = dict(
    {
        'filter_params': {
            'tariff_id': ID,
            Optional('id'): ID,
            Optional('ids'): [ID],
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('view_order', '-view_order')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

TARIFF_CONTEXT_INFO = {
    'id': ID,
    'tariff_id': ID,
    'name': NULLABLE_TEXT,
    'view_order': NON_NEGATIVE_INT,
    'context': [VIEW_TARIFF_CONTEXT_PARAM],
}

GET_TARIFF_VIEWING_CONTEXTS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'tariff_contexts': [TARIFF_CONTEXT_INFO],
            'total': NON_NEGATIVE_INT,
        }
    ),
    RESPONSE_STATUS_ERROR
)

MODIFY_VIEWING_TARIFF_CONTEXT_REQUEST = dict(
    {
        'id': int,
        Optional('new_tariff_id'): ID,
        Optional('new_name'): NULLABLE_TEXT,
        Optional('new_view_order'): NON_NEGATIVE_INT,
        Optional('new_context'): [VIEW_TARIFF_CONTEXT_PARAM],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_VIEWING_TARIFF_CONTEXT_RESPONSE = RESPONSE_STATUS_ONLY

SAVE_RULE_REQUEST = dict(
    {
        Optional('id'): int,
        'tariff_id': int,
        'tariffication_object_id': int,
        'draft_rule': TEXT,
        'status': RULE_STATUS_VALIDATOR,
        Optional('view_order'): int,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

SAVE_RULE_RESPONSE = ADDING_OBJECT_RESPONSE

GET_RULES_REQUEST = dict(
    {
        'filter_params': {
            Optional('id'): int,
            Optional('ids'): [int],
            Optional('tariff_id'): int,
            Optional('tariffication_object_id'): int,
            Optional('status'): RULE_STATUS_VALIDATOR,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id', 'view_order', '-view_order')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

RULE_INFO = {
    'id': int,
    'tariff_id': int,
    'tariff_name': TEXT,
    'tariffication_object_id': int,
    'tariffication_object_name': TEXT,
    'status': RULE_STATUS_VALIDATOR,
    'rule': NULLABLE_TEXT,
    'draft_rule': NULLABLE_TEXT,
    'view_order': int,
}

GET_RULES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'rules': [RULE_INFO],
            'total': NON_NEGATIVE_INT,
        }
    ),
    RESPONSE_STATUS_ERROR
)

DELETE_RULE_REQUEST = dict(
    {'id': int},
    **AUTHORIZED_REQUEST_AUTH_INFO
)

DELETE_RULE_RESPONSE = RESPONSE_STATUS_ONLY

APPLY_DRAFT_RULES_REQUEST = dict(
    {'tariff_id': int},
    **AUTHORIZED_REQUEST_AUTH_INFO
)

APPLY_DRAFT_RULES_RESPONSE = RESPONSE_STATUS_ONLY

PRICE_CALCULATION_CONTEXT = {
    Optional('objects_num'): POSITIVE_INT,
}

GET_TARIFFS_PRICES_REQUEST = dict(
    {
        'filter_params': {
            Optional('user_id'): int,
            Optional('ids'): [int],
            Optional('name'): TEXT,
            Optional('type'): TARIFF_TYPE_VALIDATOR,
            Optional('status'): TARIFF_STATUS_VALIDATOR,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id', 'name', '-name')],
        'calculation_contexts': [PRICE_CALCULATION_CONTEXT],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

TARIFFICATION_OBJECT_PRICE_INFO = {
    'tariffication_object_id': int,
    'tariffication_object_name': TEXT,
    'view_order': int,
    'prices': [{
        'calculation_context': PRICE_CALCULATION_CONTEXT,
        Optional('rule'): {
            'price': DECIMAL_TEXT,
            'rule_id': int,
            'rule_from_tariff_id': int,
            'rule_from_tariff_name': TEXT,
        },
        Optional('draft_rule'): {
            'price': DECIMAL_TEXT,
            'rule_id': int,
            'rule_from_tariff_id': int,
            'rule_from_tariff_name': TEXT,
        }
    }]
}

TARIFF_PRICE_INFO = {
    'tariff_id': int,
    'tariff_name': TEXT,
    'tariff_status': TARIFF_STATUS_VALIDATOR,
    'tariffication_objects': [TARIFFICATION_OBJECT_PRICE_INFO],
}

GET_TARIFFS_PRICES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'tariffs': [TARIFF_PRICE_INFO],
            'total': NON_NEGATIVE_INT,
        }
    ),
    RESPONSE_STATUS_ERROR
)

GET_PRICE_REQUEST = dict(
    {
        'tariff_id': int,
        'tariffication_object_id': int,
        Optional('user_id'): int,
        Optional('calculation_context'): PRICE_CALCULATION_CONTEXT,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_PRICE_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'tariffication_object_id': int,
            'tariffication_object_name': TEXT,
            'price': DECIMAL_TEXT,
            'rule_id': int,
            'rule_from_tariff_id': int,
            'rule_from_tariff_name': TEXT,
            Optional('calculation_context'): PRICE_CALCULATION_CONTEXT
        }
    ),
    RESPONSE_STATUS_ERROR
)

GET_DRAFT_PRICE_REQUEST = GET_PRICE_REQUEST

GET_DRAFT_PRICE_RESPONSE = GET_PRICE_RESPONSE

ADD_USER_TARIFF_REQUEST = dict(
    {
        'tariff_id': int,
        'user_id': int,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_USER_TARIFF_RESPONSE = ADDING_OBJECT_RESPONSE

DELETE_USER_TARIFFS_REQUEST = dict(
    {'user_id': int, 'tariff_ids': [int]},
    **AUTHORIZED_REQUEST_AUTH_INFO
)

DELETE_USER_TARIFFS_RESPONSE = RESPONSE_STATUS_ONLY

GET_USER_TARIFFS_REQUEST = dict(
    {
        'filter_params': {
            Optional('user_ids'): [int],
            Optional('tariff_ids'): [int],
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_USER_TARIFFS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'user_tariffs': [{'user_id': int, 'tariff_ids': [int]}],
            'total': NON_NEGATIVE_INT,
        }
    ),
    RESPONSE_STATUS_ERROR
)


protocol = [

    ApiCall('ping_request', Scheme(PING_REQUEST)),
    ApiCall('ping_response', Scheme(PING_RESPONSE)),

    # login user
    ApiCall('login_request', Scheme(LOGIN_REQUEST)),
    ApiCall('login_response', Scheme(LOGIN_RESPONSE)),

    # logout user
    ApiCall('logout_request', Scheme(LOGOUT_REQUEST)),
    ApiCall('logout_response', Scheme(LOGOUT_RESPONSE)),

    # tariffication object
    ApiCall('add_tariffication_object_request', Scheme(ADD_TARIFFICATION_OBJECT_REQUEST)),
    ApiCall('add_tariffication_object_response', Scheme(ADD_TARIFFICATION_OBJECT_RESPONSE)),

    ApiCall('get_tariffication_objects_request', Scheme(GET_TARIFFICATION_OBJECTS_REQUEST)),
    ApiCall('get_tariffication_objects_response', Scheme(GET_TARIFFICATION_OBJECTS_RESPONSE)),

    ApiCall('modify_tariffication_object_request', Scheme(MODIFY_TARIFFICATION_OBJECT_REQUEST)),
    ApiCall('modify_tariffication_object_response', Scheme(MODIFY_TARIFFICATION_OBJECT_RESPONSE)),

    ApiCall('delete_tariffication_object_request', Scheme(DELETE_TARIFFICATION_OBJECT_REQUEST)),
    ApiCall('delete_tariffication_object_response', Scheme(DELETE_TARIFFICATION_OBJECT_RESPONSE)),

    # tariff
    ApiCall('add_tariff_request', Scheme(ADD_TARIFF_REQUEST)),
    ApiCall('add_tariff_response', Scheme(ADD_TARIFF_RESPONSE)),

    ApiCall('get_tariffs_request', Scheme(GET_TARIFFS_REQUEST)),
    ApiCall('get_tariffs_response', Scheme(GET_TARIFFS_RESPONSE)),

    ApiCall('modify_tariff_request', Scheme(MODIFY_TARIFF_REQUEST)),
    ApiCall('modify_tariff_response', Scheme(MODIFY_TARIFF_RESPONSE)),

    ApiCall('delete_tariff_request', Scheme(DELETE_TARIFF_REQUEST)),
    ApiCall('delete_tariff_response', Scheme(DELETE_TARIFF_RESPONSE)),

    # rules
    ApiCall('save_rule_request', Scheme(SAVE_RULE_REQUEST)),
    ApiCall('save_rule_response', Scheme(SAVE_RULE_RESPONSE)),

    ApiCall('get_rules_request', Scheme(GET_RULES_REQUEST)),
    ApiCall('get_rules_response', Scheme(GET_RULES_RESPONSE)),

    ApiCall('delete_rule_request', Scheme(DELETE_RULE_REQUEST)),
    ApiCall('delete_rule_response', Scheme(DELETE_RULE_RESPONSE)),

    ApiCall('apply_draft_rules_request', Scheme(APPLY_DRAFT_RULES_REQUEST)),
    ApiCall('apply_draft_rules_response', Scheme(APPLY_DRAFT_RULES_RESPONSE)),

    # pricing
    ApiCall('get_price_request', Scheme(GET_PRICE_REQUEST)),
    ApiCall('get_price_response', Scheme(GET_PRICE_RESPONSE)),

    ApiCall('get_draft_price_request', Scheme(GET_DRAFT_PRICE_REQUEST)),
    ApiCall('get_draft_price_response', Scheme(GET_DRAFT_PRICE_RESPONSE)),

    ApiCall('get_tariffs_prices_request', Scheme(GET_TARIFFS_PRICES_REQUEST)),
    ApiCall('get_tariffs_prices_response', Scheme(GET_TARIFFS_PRICES_RESPONSE)),

    # user tariff
    ApiCall('add_user_tariff_request', Scheme(ADD_USER_TARIFF_REQUEST)),
    ApiCall('add_user_tariff_response', Scheme(ADD_USER_TARIFF_RESPONSE)),

    ApiCall('delete_user_tariffs_request', Scheme(DELETE_USER_TARIFFS_REQUEST)),
    ApiCall('delete_user_tariffs_response', Scheme(DELETE_USER_TARIFFS_RESPONSE)),

    ApiCall('get_user_tariffs_request', Scheme(GET_USER_TARIFFS_REQUEST)),
    ApiCall('get_user_tariffs_response', Scheme(GET_USER_TARIFFS_RESPONSE)),

    # viewing tariff context
    ApiCall('add_tariff_viewing_context_request', Scheme(ADD_TARIFF_VIEWING_CONTEXT_REQUEST)),
    ApiCall('add_tariff_viewing_context_response', Scheme(ADD_TARIFF_VIEWING_CONTEXT_RESPONSE)),

    ApiCall('get_tariff_viewing_contexts_request', Scheme(GET_TARIFF_VIEWING_CONTEXTS_REQUEST)),
    ApiCall('get_tariff_viewing_contexts_response', Scheme(GET_TARIFF_VIEWING_CONTEXTS_RESPONSE)),

    ApiCall('modify_viewing_tariff_context_request', Scheme(MODIFY_VIEWING_TARIFF_CONTEXT_REQUEST)),
    ApiCall('modify_viewing_tariff_context_response', Scheme(MODIFY_VIEWING_TARIFF_CONTEXT_RESPONSE)),

    # action log
    ApiCall('get_action_logs_request', Scheme(GET_ACTION_LOGS_REQUEST)),
    ApiCall('get_action_logs_response', Scheme(GET_ACTION_LOGS_RESPONSE)),

    ApiCall('get_action_logs_self_request', Scheme(GET_ACTION_LOGS_SELF_REQUEST)),
    ApiCall('get_action_logs_self_response', Scheme(GET_ACTION_LOGS_SELF_RESPONSE)),

]
