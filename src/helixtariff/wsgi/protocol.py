from helixcore.server.api import ApiCall
from helixcore.json_validator import (Scheme, Text, Optional, AnyOf,
    NonNegative, NullableText, DecimalText, Positive)
from helixcore.server.protocol_primitives import (PING_REQUEST, PING_RESPONSE,
    LOGIN_REQUEST, LOGIN_RESPONSE, LOGOUT_REQUEST, LOGOUT_RESPONSE,
    AUTHORIZED_REQUEST_AUTH_INFO, ADDING_OBJECT_RESPONSE, RESPONSE_STATUS_ONLY,
    GET_ACTION_LOGS_REQUEST, GET_ACTION_LOGS_RESPONSE,
    GET_ACTION_LOGS_SELF_REQUEST, GET_ACTION_LOGS_SELF_RESPONSE,
    REQUEST_PAGING_PARAMS, RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR)


TariffParentIdValidator = AnyOf(None, int)
TariffTypeValidator = AnyOf('public', 'personal')
TariffStatusValidator = AnyOf('active', 'archive', 'inactive')
RuleStatusValidator = AnyOf('active', 'inactive')


ADD_TARIFFICATION_OBJECT_REQUEST = dict(
    {'name': Text()},
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_TARIFFICATION_OBJECT_RESPONSE = ADDING_OBJECT_RESPONSE

GET_TARIFFICATION_OBJECTS_REQUEST = dict(
    {
        'filter_params': {
            Optional('id'): int,
            Optional('ids'): [int],
            Optional('name'): Text(),
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

TARIFFICATION_OBJECT_INFO = {
    'id': int,
    'name': Text(),
}

GET_TARIFFICATION_OBJECTS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'tariffication_objects': [TARIFFICATION_OBJECT_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

MODIFY_TARIFFICATION_OBJECT_REQUEST = dict(
    {
        'id': int,
        'new_name': Text(),
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
        'name': Text(),
        'parent_tariff_id': TariffParentIdValidator,
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
            Optional('name'): Text(),
            Optional('type'): TariffTypeValidator,
            Optional('status'): TariffStatusValidator,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id', 'name', '-name')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

TARIFF_INFO = {
    'id': int,
    'name': Text(),
    'parent_tariffs': [{'id': int, 'name': Text(), 'status': TariffStatusValidator}],
    'type': TariffTypeValidator,
    'status': TariffStatusValidator,
}

GET_TARIFFS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'tariffs': [TARIFF_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

MODIFY_TARIFF_REQUEST = dict(
    {
        'id': int,
        Optional('new_name'): Text(),
        Optional('new_parent_tariff_id'): TariffParentIdValidator,
        Optional('new_type'): TariffTypeValidator,
        Optional('new_status'): TariffStatusValidator,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_TARIFF_RESPONSE = RESPONSE_STATUS_ONLY

DELETE_TARIFF_REQUEST = dict(
    {'id': int},
    **AUTHORIZED_REQUEST_AUTH_INFO
)

DELETE_TARIFF_RESPONSE = RESPONSE_STATUS_ONLY

SAVE_RULE_REQUEST = dict(
    {
        Optional('id'): int,
        'tariff_id': int,
        'tariffication_object_id': int,
        'draft_rule': Text(),
        'status': RuleStatusValidator,
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
            Optional('status'): RuleStatusValidator,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id', 'view_order', '-view_order')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

RULE_INFO = {
    'id': int,
    'tariff_id': int,
    'tariff_name': Text(),
    'tariffication_object_id': id,
    'tariffication_object_name': Text(),
    'status': RuleStatusValidator,
    'rule': NullableText(),
    'draft_rule': NullableText(),
    'view_order': int,
}

GET_RULES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'rules': [RULE_INFO],
            'total': NonNegative(int),
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

APPLY_DRAFT_RULE_RESPONSE = RESPONSE_STATUS_ONLY

PRICE_CALCULATION_CONTEXT = {
    Optional('objects_num'): Positive(int),
}

GET_TARIFFS_PRICES_REQUEST = dict(
    {
        'filter_params': {
            Optional('user_ids'): [int],
            Optional('tariff_ids'): [int],
            Optional('calculation_contexts'): [PRICE_CALCULATION_CONTEXT],
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('view_order', '-view_order')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

PRICE_INFO = {
    'tariffication_object_id': int,
    'tariffication_object_name': Text(),
    Optional('rule'): {
        'id': int,
        'status': RuleStatusValidator,
        'rule_from_tariff_id': int,
        'rule_from_tariff_name': Text(),
        'price': DecimalText(),
    },
    Optional('draft_rule'): {
        'id': int,
        'status': RuleStatusValidator,
        'rule_from_tariff_id': int,
        'rule_from_tariff_name': Text(),
        'price': DecimalText(),
    }
}

GET_TARIFFS_PRICES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'prices': [PRICE_INFO],
            'total': NonNegative(int),
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
            'price': DecimalText(),
            'rule_id': int,
            'tariffication_object_id': int,
            'tariffication_object_name': Text(),
            'rule_from_tariff_id': int,
            'rule_from_tariff_name': Text(),
            Optional('calculation_context'): PRICE_CALCULATION_CONTEXT
        }
    ),
    RESPONSE_STATUS_ERROR
)

GET_DRAFT_PRICE_REQUEST = GET_PRICE_REQUEST

GET_DRAFT_PRICE_RESPONSE = GET_PRICE_RESPONSE


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
    ApiCall('apply_draft_rules_response', Scheme(APPLY_DRAFT_RULE_RESPONSE)),

    # pricing
    ApiCall('get_price_request', Scheme(GET_PRICE_REQUEST)),
    ApiCall('get_price_response', Scheme(GET_PRICE_RESPONSE)),

    ApiCall('get_draft_price_request', Scheme(GET_DRAFT_PRICE_REQUEST)),
    ApiCall('get_draft_price_response', Scheme(GET_DRAFT_PRICE_RESPONSE)),

    ApiCall('get_tariffs_prices_request', Scheme(GET_TARIFFS_PRICES_REQUEST)),
    ApiCall('get_tariffs_prices_response', Scheme(GET_TARIFFS_PRICES_RESPONSE)),

    # action log
    ApiCall('get_action_logs_request', Scheme(GET_ACTION_LOGS_REQUEST)),
    ApiCall('get_action_logs_response', Scheme(GET_ACTION_LOGS_RESPONSE)),

    ApiCall('get_action_logs_self_request', Scheme(GET_ACTION_LOGS_SELF_REQUEST)),
    ApiCall('get_action_logs_self_response', Scheme(GET_ACTION_LOGS_SELF_RESPONSE)),

]
