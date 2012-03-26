# coding=utf-8
import unittest
import pytz
import datetime

from helixcore.server.api import Api
from helixcore.test.utils_for_testing import ProtocolTester

from helixtariff.test.root_test import RootTestCase
from helixtariff.wsgi.protocol import protocol
from helixtariff.db.dataobject import Tariff, Rule


class ProtocolTestCase(RootTestCase, ProtocolTester):
    api = Api(protocol)

    def test_login(self):
        a_name = 'login'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'environment_name': 'e', 'custom_actor_info': 'i'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'environment_name': 'n'})

        self.api.validate_response(a_name, {'status': 'ok', 'session_id': 'i',
            'user_id': 5, 'environment_id': 7})
        self.validate_error_response(a_name)

    def test_logout(self):
        a_name = 'logout'
        self.api.validate_request(a_name, {'session_id': 'i'})
        self.validate_status_response(a_name)

    def test_add_tariffication_object(self):
        a_name = 'add_tariffication_object'
        self.api.validate_request(a_name, {'session_id': 's', 'name': 'one'})
        self.api.validate_request(a_name, {'session_id': 's',
            'name': u'лунный свет'})
        self.api.validate_response(a_name, {'status': 'ok', 'id': 1})
        self.validate_error_response(a_name)

    def test_get_tariffication_objects(self):
        a_name = 'get_tariffication_objects'
        self.api.validate_request(a_name, {'session_id': 'i',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 'i',
            'filter_params': {'id': 1, 'ids': [1, 2], 'name': 'lala'},
            'paging_params': {'limit': 0, 'offset': 0,}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariffication_objects': [
                {'id': 1, 'name': 'one'},
                {'id': 2, 'name': 'two'},
            ]
        })
        self.validate_error_response(a_name)

    def test_modify_tariffication_object(self):
        a_name = 'modify_tariffication_object'
        self.api.validate_request(a_name, {'session_id': 's',
            'id': 1, 'new_name': 'one'})
        self.validate_status_response(a_name)

    def test_delete_tariffication_object(self):
        a_name = 'delete_tariffication_object'
        self.api.validate_request(a_name, {'session_id': 's', 'id': 1})
        self.validate_status_response(a_name)

    def test_get_action_logs(self):
        a_name = 'get_action_logs'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'from_request_date': '2011-02-21 00:00:00',
            'to_request_date': '2011-02-21 23:59:59'},
            'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'action': 'a'}, 'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'user_id': 1}, 'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'session_id': ''}, 'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'action_logs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'action_logs': [
            {
                'id': 42, 'session_id': 's_id', 'custom_actor_info': None,
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.1', 'request': 'req',
                'response': 'resp'
            },
        ]})
        self.validate_error_response(a_name)

    def test_get_action_logs_self(self):
        a_name = 'get_action_logs_self'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'from_request_date': '2011-02-21 00:00:00',
            'to_request_date': '2011-02-21 23:59:59'},
            'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'action': 'a'}, 'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'session_id': ''}, 'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'action_logs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'action_logs': [
            {
                'id': 42, 'session_id': 's_id', 'custom_actor_info': None,
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.1', 'request': 'req',
                'response': 'resp'
            },
        ]})
        self.validate_error_response(a_name)

    def test_add_tariff(self):
        a_name = 'add_tariff'
        self.api.validate_request(a_name, {'session_id': 's', 'name': 'one',
            'parent_tariff_id': None,
            'type': Tariff.TYPE_PERSONAL, 'status': Tariff.STATUS_ACTIVE})
        self.api.validate_request(a_name, {'session_id': 's', 'name': 'one',
            'parent_tariff_id': 1, 'currency': 'RUB',
            'type': Tariff.TYPE_PUBLIC, 'status': Tariff.STATUS_INACTIVE})

        self.api.validate_response(a_name, {'status': 'ok', 'id': 1})
        self.validate_error_response(a_name)

    def test_get_tariffs(self):
        a_name = 'get_tariffs'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'id': 1, 'ids': [1, 2], 'name': 't',
            'type': Tariff.TYPE_PERSONAL, 'status': Tariff.STATUS_ARCHIVE},
            'paging_params': {'limit': 0}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariffs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariffs': [
                {'id': 1, 'name': 't0', 'parent_tariffs': [{'id': 1, 'name': 'pt0',
                'status': Tariff.STATUS_ACTIVE, 'currency': 'RUB'}], 'type': Tariff.TYPE_PUBLIC,
                'status': Tariff.STATUS_ACTIVE, 'currency': 'RUB'}
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariffs': [
                {'id': 1, 'name': 't0', 'parent_tariffs': [{'id': 2, 'name': 'pt2',
                'status': Tariff.STATUS_ACTIVE, 'currency': None}, {'id': 3, 'name': 'pt3',
                'status': Tariff.STATUS_ARCHIVE, 'currency': 'RUB'}],
                'type': Tariff.TYPE_PUBLIC, 'status': Tariff.STATUS_ACTIVE, 'currency': 'RUB'},
                {'id': 1, 'name': 't0', 'parent_tariffs': [{'id': 1, 'name': 'pt0',
                'status': Tariff.STATUS_ACTIVE, 'currency': None}], 'type': Tariff.TYPE_PUBLIC,
                'status': Tariff.STATUS_ACTIVE, 'currency': None},
        ]})
        self.validate_error_response(a_name)

    def test_modify_tariff(self):
        a_name = 'modify_tariff'
        self.api.validate_request(a_name, {'session_id': 's', 'id': 1, 'new_name': 'n'})
        self.api.validate_request(a_name, {'session_id': 's', 'id': 1,
            'new_name': 'n', 'new_status': Tariff.STATUS_ARCHIVE,
            'new_type': Tariff.TYPE_PERSONAL, 'new_parent_tariff_id': 1,
            'new_currency': 'RUB'})
        self.api.validate_request(a_name, {'session_id': 's', 'id': 1,
            'new_currency': None})
        self.validate_status_response(a_name)

    def test_delete_tariff(self):
        a_name = 'delete_tariff'
        self.api.validate_request(a_name, {'session_id': 's', 'id': 1})
        self.validate_status_response(a_name)

    def test_add_viewing_tariff_context(self):
        a_name = 'add_tariff_viewing_context'
        self.api.validate_request(a_name, {'session_id': 's', 'name': None,
            'tariff_id': 1, 'view_order': 2, 'context': []})
        self.api.validate_request(a_name, {'session_id': 's', 'name': None,
            'tariff_id': 1, 'view_order': 2, 'context': [
                {'name': 'num', 'value': 2},
                {'name': 'num', 'value': 3},
                {'name': 'name', 'value': 'n'},
            ]})

        self.api.validate_response(a_name, {'status': 'ok', 'id': 1})
        self.validate_error_response(a_name)

    def test_get_tariff_viewing_contexts(self):
        a_name = 'get_tariff_viewing_contexts'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'tariff_id': 4}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'id': 1, 'ids': [1, 2], 'tariff_id': 2},
            'paging_params': {'limit': 0},
            'ordering_params': ['view_order']})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariff_contexts': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariff_contexts': [
                {'id': 1, 'name': 't0', 'tariff_id': 3, 'view_order': 3,
                'context': [
                    {'name': 'n', 'value': 'v'},
                    {'name': 'm', 'value': 1},
                ]}
            ]})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariff_contexts': [
                {'id': 1, 'name': 't0', 'tariff_id': 3, 'view_order': 3,
                'context': [
                    {'name': 'n', 'value': 'v'},
                    {'name': 'm', 'value': 1},
                ]},
                {'id': 1, 'name': 't0', 'tariff_id': 3, 'view_order': 4,
                'context': [
                    {'name': 'n', 'value': 'v'},
                    {'name': 'm', 'value': 1},
                ]}
            ]})
        self.validate_error_response(a_name)

    def test_modify_viewing_tariff_context(self):
        a_name = 'modify_tariff_viewing_context'
        self.api.validate_request(a_name, {'session_id': 's', 'id': 1,
            'new_name': 'n'})
        self.api.validate_request(a_name, {'session_id': 's', 'id': 1,
            'new_name': 'n', 'new_tariff_id': 4,
            'new_view_order': 3, 'new_context': [
                {'name': 'num', 'value': 2},
            ]})

        self.validate_status_response(a_name)

    def test_delete_viewing_tariff_context(self):
        a_name = 'delete_tariff_viewing_context'
        self.api.validate_request(a_name, {'session_id': 's', 'id': 1})
        self.validate_status_response(a_name)

    def test_save_rules(self):
        a_name = 'save_rule'
        self.api.validate_request(a_name, {'session_id': 's', 'tariff_id': 1,
            'tariffication_object_id': 3, 'draft_rule': 'p',
            'status': Rule.STATUS_ACTIVE})
        self.api.validate_request(a_name, {'session_id': 's', 'tariff_id': 1,
            'tariffication_object_id': 3, 'draft_rule': 'p',
            'status': Rule.STATUS_ACTIVE, 'view_order': 0})

        self.api.validate_response(a_name, {'status': 'ok', 'id': 1})
        self.validate_error_response(a_name)

    def test_get_rules(self):
        a_name = 'get_rules'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'id': 1, 'ids': [1, 2],
            'tariff_id': 1, 'tariffication_object_id': 1,
            'status': Rule.STATUS_ACTIVE},
            'paging_params': {'limit': 0}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'rules': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'rules': [
                {'id': 1, 'tariff_id': 1, 'tariff_name': 't0',
                'tariffication_object_id': 2, 'tariffication_object_name': 'to0',
                'rule': None, 'draft_rule': 'rule', 'status': Rule.STATUS_ACTIVE,
                'view_order': 0},
                {'id': 1, 'tariff_id': 1, 'tariff_name': 't0',
                'tariffication_object_id': 2, 'tariffication_object_name': 'to0',
                'rule': 'tt', 'draft_rule': None, 'status': Rule.STATUS_ACTIVE,
                'view_order': 1}
            ]
        })
        self.validate_error_response(a_name)

    def test_delete_rule(self):
        a_name = 'delete_rule'
        self.api.validate_request(a_name, {'session_id': 's', 'id': 1})
        self.validate_status_response(a_name)

    def test_apply_rules(self):
        a_name = 'apply_draft_rules'
        self.api.validate_request(a_name, {'session_id': 's', 'tariff_id': 1})
        self.validate_status_response(a_name)

    def test_get_tariffs_prices(self):
        a_name = 'get_tariffs_prices'
        self.api.validate_request(a_name, {'session_id': 's', 'filter_params': {},
            'paging_params': {}, 'calculation_contexts': []})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'user_id': 1, 'ids': [1, 2]},
            'paging_params': {'limit': 0}, 'calculation_contexts': []})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'user_id': 1, 'ids': [1, 2]},
            'paging_params': {'limit': 0}, 'calculation_contexts': [{'objects_num': 3}]})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariffs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariffs': [{
                'tariff_id': 1, 'tariff_name': 't0', 'tariff_status': Tariff.STATUS_ACTIVE,
                'tariffication_objects': [
                    {'tariffication_object_id': 2, 'tariffication_object_name': 'to0',
                        'view_order': 1,
                        'prices': [
                            {'calculation_context': {},
                             'rule': {'rule_id': 1, 'rule_from_tariff_id': 1,
                                 'rule_from_tariff_name': 't0', 'price': '10.1'}
                             }
                        ],
                    }
                ]
            }]
        })
        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariffs': [{
                'tariff_id': 1, 'tariff_name': 't0', 'tariff_status': Tariff.STATUS_ACTIVE,
                'tariffication_objects': [
                    {'tariffication_object_id': 2, 'tariffication_object_name': 'to0',
                        'view_order': 1,
                        'prices': [
                            {'calculation_context': {},
                                 'draft_rule': {'rule_id': 1, 'rule_from_tariff_id': 1,
                                     'rule_from_tariff_name': 't0', 'price': '10.1'},
                                 'rule': {'rule_id': 1, 'rule_from_tariff_id': 1,
                                     'rule_from_tariff_name': 't0', 'price': '10.1'},
                             }
                        ],
                    }
                ]
            }]
        })
        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariffs': [
                {'tariff_id': 1, 'tariff_name': 't0', 'tariff_status': Tariff.STATUS_ACTIVE,
                'tariffication_objects': [
                    {'tariffication_object_id': 2, 'tariffication_object_name': 'to0',
                        'view_order': 1,
                        'prices': [
                            {'calculation_context': {},
                                 'draft_rule': {'rule_id': 1, 'rule_from_tariff_id': 1,
                                     'rule_from_tariff_name': 't0', 'price': '10.1'},
                                 'rule': {'rule_id': 1, 'rule_from_tariff_id': 1,
                                     'rule_from_tariff_name': 't0', 'price': '10.2'},
                             }
                        ],
                    }
                ]},
                {'tariff_id': 12, 'tariff_name': 't02', 'tariff_status': Tariff.STATUS_ARCHIVE,
                'tariffication_objects': [
                    {'tariffication_object_id': 2, 'tariffication_object_name': 'to0',
                        'view_order': 2,
                        'prices': [
                            {'calculation_context': {},
                                 'draft_rule': {'rule_id': 1, 'rule_from_tariff_id': 1,
                                     'rule_from_tariff_name': 't0', 'price': '10.1'},
                                 'rule': {'rule_id': 1, 'rule_from_tariff_id': 1,
                                     'rule_from_tariff_name': 't0', 'price': '10.1'},
                             },
                            {'calculation_context': {'objects_num': 100},
                                 'draft_rule': {'rule_id': 1, 'rule_from_tariff_id': 1,
                                     'rule_from_tariff_name': 't0', 'price': '8.1'},
                                 'rule': {'rule_id': 1, 'rule_from_tariff_id': 1,
                                     'rule_from_tariff_name': 't0', 'price': '7.1'},
                             }
                        ],
                    }
                ]},
            ]
        })

    def test_get_price(self):
        a_name = 'get_price'
        self.api.validate_request(a_name, {'session_id': 's',
            'tariff_id': 1, 'tariffication_object_id': 3})

        self.api.validate_response(a_name, {'status': 'ok',
            'price': '10.1', 'rule_id': 1,
            'tariffication_object_id': 2, 'tariffication_object_name': 'to0',
            'rule_from_tariff_id': 1, 'rule_from_tariff_name': 't0',
        })
        self.api.validate_response(a_name, {'status': 'ok',
            'price': '10.1', 'rule_id': 1,
            'tariffication_object_id': 2, 'tariffication_object_name': 'to0',
            'rule_from_tariff_id': 1, 'rule_from_tariff_name': 't0',
            'calculation_context': {'objects_num': 3}
        })
        self.validate_error_response(a_name)

    def test_get_draft_price(self):
        a_name = 'get_draft_price'
        self.api.validate_request(a_name, {'session_id': 's',
            'tariff_id': 1, 'tariffication_object_id': 3})

        self.api.validate_response(a_name, {'status': 'ok',
            'price': '10.1', 'rule_id': 1,
            'tariffication_object_id': 2, 'tariffication_object_name': 'to0',
            'rule_from_tariff_id': 1, 'rule_from_tariff_name': 't0',
        })
        self.api.validate_response(a_name, {'status': 'ok',
            'price': '10.1', 'rule_id': 1,
            'tariffication_object_id': 2, 'tariffication_object_name': 'to0',
            'rule_from_tariff_id': 1, 'rule_from_tariff_name': 't0',
            'calculation_context': {'objects_num': 3}
        })
        self.validate_error_response(a_name)

    def test_add_user_tariff(self):
        a_name = 'add_user_tariff'
        self.api.validate_request(a_name, {'session_id': 's',
            'tariff_id': 1, 'user_id': 2})

        self.api.validate_response(a_name, {'status': 'ok', 'id': 1})
        self.validate_error_response(a_name)

    def test_delete_user_tariffs(self):
        a_name = 'delete_user_tariffs'
        self.api.validate_request(a_name, {'session_id': 's', 'user_id': 1,
            'tariff_ids': [1, 2]})
        self.validate_status_response(a_name)

    def test_get_users_tariffs(self):
        a_name = 'get_user_tariffs'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'user_ids': [1], 'tariff_ids': [1, 2]},
            'paging_params': {'limit': 0}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'user_tariffs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'user_tariffs': [{'user_id': 1, 'tariff_ids': [1, 2]}]})
        self.validate_error_response(a_name)


if __name__ == '__main__':
    unittest.main()
