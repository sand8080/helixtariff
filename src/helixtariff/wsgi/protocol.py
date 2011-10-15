from helixcore.server.api import ApiCall
from helixcore.json_validator import (Scheme, Text, Optional, AnyOf,
    NonNegative)
from helixcore.server.protocol_primitives import (PING_REQUEST, PING_RESPONSE,
    LOGIN_REQUEST, LOGIN_RESPONSE, LOGOUT_REQUEST, LOGOUT_RESPONSE,
    AUTHORIZED_REQUEST_AUTH_INFO, ADDING_OBJECT_RESPONSE, RESPONSE_STATUS_ONLY,
    GET_ACTION_LOGS_REQUEST, GET_ACTION_LOGS_RESPONSE,
    GET_ACTION_LOGS_SELF_REQUEST, GET_ACTION_LOGS_SELF_RESPONSE,
    REQUEST_PAGING_PARAMS, RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR,
    ADDING_OBJECTS_RESPONSE)


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

SAVE_RULES_REQUEST = dict(
    {'rules':[
        {
            Optional('id'): int,
            'tariff_id': int,
            'tariffication_object_id': int,
            'draft_rule': Text(),
            'status': RuleStatusValidator,
        }
    ]},
    **AUTHORIZED_REQUEST_AUTH_INFO
)

SAVE_RULES_RESPONSE = ADDING_OBJECTS_RESPONSE

## --- service set ---
#ADD_SERVICE_SET = dict(
#    {
#        'name': Text(),
#        'service_types': [Text()],
#    },
#    **AUTH_INFO
#)
#
#MODIFY_SERVICE_SET = dict(
#    {
#        'name': Text(),
#        Optional('new_name'): Text(),
#        Optional('new_service_types'): [Text()],
#    },
#    **AUTH_INFO
#)
#
#DELETE_SERVICE_SET = dict(
#    {'name': Text()},
#    **AUTH_INFO
#)
#
#SERVICE_SET_INFO = dict({
#    'name': Text(),
#    'service_types': [Text()],
#})
#
#GET_SERVICE_SET = dict(
#    {'name': Text()},
#    **AUTH_INFO
#)
#
#GET_SERVICE_SET_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **SERVICE_SET_INFO
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#VIEW_SERVICE_SETS = AUTH_INFO
#
#VIEW_SERVICE_SETS_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **{'service_sets': [SERVICE_SET_INFO]}
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#GET_SERVICE_SET_DETAILED = GET_SERVICE_SET
#SERVICE_SET_INFO_DETAILED = dict({'tariffs': [Text()]}, **SERVICE_SET_INFO)
#
#GET_SERVICE_SET_DETAILED_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **SERVICE_SET_INFO_DETAILED
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#VIEW_SERVICE_SETS_DETAILED = VIEW_SERVICE_SETS
#
#VIEW_SERVICE_SETS_DETAILED_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **{'service_sets': [SERVICE_SET_INFO_DETAILED]}
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#


#MODIFY_TARIFF = dict(
#    {
#        'name': Text(),
#        Optional('new_name'): Text(),
#        Optional('new_parent_tariff'): NullableText,
#        Optional('new_in_archive'): bool,
#        Optional('new_service_set'): Text(),
#    },
#    **AUTH_INFO
#)
#
#DELETE_TARIFF = dict(
#    {'name': Text()},
#    **AUTH_INFO
#)
#
#TARIFF_INFO = {
#    'name': Text(),
#    'service_set': Text(),
#    'parent_tariff': NullableText,
#    'tariffs_chain': [Text()],
#    'in_archive': bool,
#}
#
#GET_TARIFF = dict(
#    {'name': Text()},
#    **AUTH_INFO
#)
#
#GET_TARIFF_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **TARIFF_INFO
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#GET_TARIFF_DETAILED = GET_TARIFF
#
#DETAILED_TARIFF_INFO = dict(
#    {'service_types': [Text()]},
#    **TARIFF_INFO
#)
#
#GET_TARIFF_DETAILED_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **DETAILED_TARIFF_INFO
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#VIEW_TARIFFS = AUTH_INFO
#
#VIEW_TARIFFS_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **{'tariffs': [TARIFF_INFO]}
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#VIEW_TARIFFS_DETAILED = VIEW_TARIFFS
#VIEW_TARIFFS_DETAILED_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **{'tariffs': [DETAILED_TARIFF_INFO]}
#    ),
#    RESPONSE_STATUS_ERROR
#)


## --- rule ---
#SAVE_DRAFT_RULE = dict(
#    {
#        'tariff': Text(),
#        'service_type': Text(),
#        'rule': Text(),
#        'enabled': bool,
#    },
#    **AUTH_INFO
#)
#
#DELETE_DRAFT_RULE = dict(
#    {
#        'tariff': Text(),
#        'service_type': Text(),
#    },
#    **AUTH_INFO
#)
#
#MAKE_DRAFT_RULES_ACTUAL = dict(
#    {'tariff': Text()},
#    **AUTH_INFO
#)
#
#MODIFY_ACTUAL_RULE = dict(
#    {
#        'tariff': Text(),
#        'service_type': Text(),
#        'new_enabled': bool,
#    },
#    **AUTH_INFO
#)
#
#RULE_TYPES = AnyOf(Rule.TYPE_ACTUAL, Rule.TYPE_DRAFT)
#
#GET_RULE = dict(
#    {
#        'tariff': Text(),
#        'service_type': Text(),
#        'type': RULE_TYPES
#    },
#    **AUTH_INFO
#)
#
#RULE_INFO = {
#    'service_type': Text(),
#    'rule': Text(),
#    'type': RULE_TYPES,
#    'enabled': bool,
#}
#
#GET_RULE_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **dict({'tariff': Text()}, **RULE_INFO)
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#VIEW_RULES = dict(
#    {'tariff': Text()},
#    **AUTH_INFO
#)
#
#VIEW_RULES_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **{
#            'tariff': Text(),
#            'rules': [RULE_INFO],
#        }
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#
## --- price ---
#GET_PRICE = dict(
#    {
#        'tariff': Text(),
#        'service_type': Text(),
#        Optional('context'): FlatDict(),
#    },
#    **AUTH_INFO
#)
#
#PRICE_CALC_NORMAL = 'normal'
#PRICE_CALC_SERVICE_TYPE_DISABLED = 'service_type_disabled'
#PRICE_CALC_PRICE_UNDEFINED = 'price_undefined'
#PRICE_CALC_RULE_DISABLED = 'rule_disabled'
#PRICE_CALCULATION = AnyOf(
#    PRICE_CALC_NORMAL,
#    PRICE_CALC_SERVICE_TYPE_DISABLED,
#    PRICE_CALC_PRICE_UNDEFINED,
#    PRICE_CALC_RULE_DISABLED,
#)
#
#PRICE_INFO= {
#    'service_type': Text(),
#    'tariffs_chain': [Text()],
#    'price': AnyOf(DecimalText(), None),
#    'price_calculation': PRICE_CALCULATION,
#    'draft_tariffs_chain': [Text()],
#    'draft_price': AnyOf(DecimalText(), None),
#    'draft_price_calculation': PRICE_CALCULATION,
#}
#
#GET_PRICE_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **dict(
#            {
#                'tariff': Text(),
#                'context': FlatDict(),
#            },
#            **PRICE_INFO
#        )
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#VIEW_PRICES = dict(
#    {
#        'tariff': Text(),
#        Optional('context'): FlatDict(),
#    },
#    **AUTH_INFO
#)
#
#VIEW_PRICES_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **{
#            'tariff': Text(),
#            'context': FlatDict(),
#            'prices': [PRICE_INFO],
#        }
#    ),
#    RESPONSE_STATUS_ERROR
#)
#
#
## --- action log ---
#VIEW_ACTION_LOGS = dict(
#    {
#        'filter_params': {
#            Optional('action'): Text(),
#            Optional('limit'): NonNegative(int),
#            Optional('offset'): NonNegative(int),
#            Optional('from_date'): IsoDatetime(),
#            Optional('to_date'): IsoDatetime(),
#        },
#    },
#    **AUTH_INFO
#)
#
#ACTION_LOG_INFO = {
#    'custom_operator_info': NullableText,
#    'action': Text(),
#    'request_date': IsoDatetime(),
#    'remote_addr': NullableText,
#    'request': Text(),
#    'response': Text(),
#}
#
#
#VIEW_ACTION_LOGS_RESPONSE = AnyOf(
#    dict(
#        RESPONSE_STATUS_OK,
#        **{
#            'total': NonNegative(int),
#            'action_logs': [ACTION_LOG_INFO],
#        }
#    ),
#    RESPONSE_STATUS_ERROR
#)


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

    ApiCall('save_rules_request', Scheme(SAVE_RULES_REQUEST)),
    ApiCall('save_rules_response', Scheme(SAVE_RULES_RESPONSE)),

    # action log
    ApiCall('get_action_logs_request', Scheme(GET_ACTION_LOGS_REQUEST)),
    ApiCall('get_action_logs_response', Scheme(GET_ACTION_LOGS_RESPONSE)),

    ApiCall('get_action_logs_self_request', Scheme(GET_ACTION_LOGS_SELF_REQUEST)),
    ApiCall('get_action_logs_self_response', Scheme(GET_ACTION_LOGS_SELF_RESPONSE)),

]
