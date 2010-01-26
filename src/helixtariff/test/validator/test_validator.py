# -*- coding: utf-8 -*-
from helixtariff.domain.objects import Rule
import unittest

from helixcore.test.root_test import RootTestCase
from helixcore.server.exceptions import ValidationError
from helixcore.server.api import Api

from helixtariff.validator.validator import protocol, PRICE_CALC_NORMAL,\
    PRICE_CALC_PRICE_UNDEFINED, PRICE_CALC_RULE_DISABLED


class ValidatorTestCase(RootTestCase):
    api = Api(protocol)

    def validate_status_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'ok'})
        self.api.validate_response(action_name, {'status': 'error', 'category': 'test', 'message': 'happens'})
        self.assertRaises(ValidationError, self.api.validate_response, action_name, {'status': 'error', 'category': 'test'})

    def test_ping(self):
        self.api.validate_request('ping', {})
        self.validate_status_response('ping')

    def test_add_client(self):
        self.api.validate_request('add_client', {'login': 'admin', 'password': 'crypted twice'})
        self.validate_status_response('add_client')

    def test_add_client_invalid(self):
        self.assertRaises(ValidationError, self.api.validate_request, 'add_client', {'login': 'admin'})
        self.assertRaises(ValidationError, self.api.validate_request, 'add_client', {'password': 'admin'})
        self.assertRaises(ValidationError, self.api.validate_request, 'add_client', {})

    def test_modify_client(self):
        self.api.validate_request('modify_client', {'login': 'log', 'password': 'pi', 'new_login': 'new_log'})
        self.api.validate_request('modify_client', {'login': 'log', 'password': 'pi', 'new_login': 'new_log', 'new_password': 'pw'})
        self.api.validate_request('modify_client', {'login': 'log', 'password': 'pi'})
        self.validate_status_response('modify_client')

    def test_delete_client(self):
        self.api.validate_request('delete_client', {'login': 'log', 'password': 'pi'})
        self.validate_status_response('delete_client')

    def test_add_service_type(self):
        self.api.validate_request('add_service_type', {'login': 'l', 'password': 'p', 'name': 'register_ru'})
        self.validate_status_response('add_service_type')

    def test_add_service_type_invalid(self):
        self.assertRaises(ValidationError,self.api.validate_request, 'add_service_type', {'login': 'l', 'password': 'p', 'name': 77})

    def test_modify_service_type(self):
        self.api.validate_request('modify_service_type', {'login': 'l', 'password': 'p', 'name': 'register_ru', 'new_name': 'register_RU'})
        self.validate_status_response('modify_service_type')

    def test_view_service_types(self):
        self.api.validate_request('view_service_types', {'login': 'l', 'password': 'p'})
        self.api.validate_response('view_service_types', {'status': 'ok', 'service_types': []})
        self.api.validate_response('view_service_types', {'status': 'ok', 'service_types': ['one', 'two']})
        self.api.validate_response('view_service_types', {'status': 'error', 'category': 'test', 'message': 'happens'})

    def test_view_service_types_detailed(self):
        self.api.validate_request('view_service_types_detailed', {'login': 'l', 'password': 'p'})
        self.api.validate_response('view_service_types_detailed',
            {'status': 'error', 'category': 't', 'message': 'm'})
        self.api.validate_response('view_service_types_detailed', {'status': 'ok',
            'service_types': []})
        self.api.validate_response('view_service_types_detailed', {'status': 'ok',
            'service_types': [
                {'name': 'n', 'service_sets': []},
            ]
        })
        self.api.validate_response('view_service_types_detailed', {'status': 'ok',
            'service_types': [
                {'name': 'n', 'service_sets': []},
                {'name': 'm', 'service_sets': ['s0', 's1']},
            ]
        })

    def test_modify_service_type_invalid(self):
        self.assertRaises(ValidationError, self.api.validate_request, 'modify_service_type', {'login': 'l', 'password': 'p', 'name': 'cheli0s'})

    def test_delete_service_type(self):
        self.api.validate_request('delete_service_type', {'login': 'l', 'password': 'p', 'name': 'register_ru'})
        self.validate_status_response('delete_service_type')

    def test_add_service_set(self):
        self.api.validate_request('add_service_set', {'login': 'l', 'password': 'p',
            'name': 'basic', 'service_types': []})
        self.api.validate_request('add_service_set', {'login': 'l', 'password': 'p',
            'name': 'basic', 'service_types': ['a', 'b', 'c']})
        self.validate_status_response('add_service_set')

    def test_modify_service_set(self):
        self.api.validate_request('modify_service_set', {'login': 'l', 'password': 'p',
            'name': 'basic'})
        self.api.validate_request('modify_service_set', {'login': 'l', 'password': 'p',
            'name': 'basic', 'new_name': 'restricted'})
        self.api.validate_request('modify_service_set', {'login': 'l', 'password': 'p',
            'name': 'basic', 'new_name': 'restricted', 'new_service_types': ['1', '2']})
        self.validate_status_response('modify_service_set')

    def test_delete_service_set(self):
        self.api.validate_request('delete_service_set', {'login': 'l', 'password': 'p', 'name': 'basic'})
        self.validate_status_response('delete_service_set')

    def test_get_service_set(self):
        self.api.validate_request('get_service_set',
            {'login': 'l', 'password': 'p', 'name': 't'})
        self.api.validate_response('get_service_set',
            {'status': 'error', 'category': 't', 'message': 'm'})
        self.api.validate_response('get_service_set', {'status': 'ok', 'name': 'n', 'service_types': []})
        self.api.validate_response('get_service_set', {'status': 'ok', 'name': 'n',
            'service_types': ['n']})
        self.api.validate_response('get_service_set', {'status': 'ok', 'name': 'n',
            'service_types': ['n', 'm']})

    def test_get_service_set_detailed(self):
        self.api.validate_request('get_service_set_detailed',
            {'login': 'l', 'password': 'p', 'name': 't'})
        self.api.validate_response('get_service_set_detailed',
            {'status': 'error', 'category': 't', 'message': 'm'})
        self.api.validate_response('get_service_set_detailed', {'status': 'ok', 'name': 'n',
            'service_types': [], 'tariffs': []})
        self.api.validate_response('get_service_set_detailed', {'status': 'ok', 'name': 'n',
            'service_types': ['n'], 'tariffs': []})
        self.api.validate_response('get_service_set_detailed', {'status': 'ok', 'name': 'n',
            'service_types': ['n', 'm'], 'tariffs': ['t0', 't1']})

    def test_view_service_sets(self):
        self.api.validate_request('view_service_sets',
            {'login': 'l', 'password': 'p'})
        self.api.validate_response('view_service_sets',
            {'status': 'error', 'category': 'test', 'message': 'happens'})
        self.api.validate_response('view_service_sets', {'status': 'ok', 'service_sets': []})
        self.api.validate_response('view_service_sets', {'status': 'ok',
            'service_sets': [
                {'name': 'n', 'service_types': ['n']},
            ]
        })
        self.api.validate_response('view_service_sets', {'status': 'ok',
            'service_sets': [
                {'name': 'n', 'service_types': ['n']},
                {'name': 'm', 'service_types': ['n', 'm']},
                {'name': 'l', 'service_types': []},
            ]
        })

    def test_view_service_sets_detailed(self):
        self.api.validate_request('view_service_sets_detailed',
            {'login': 'l', 'password': 'p'})
        self.api.validate_response('view_service_sets_detailed',
            {'status': 'error', 'category': 'test', 'message': 'happens'})
        self.api.validate_response('view_service_sets_detailed', {'status': 'ok',
            'service_sets': []})
        self.api.validate_response('view_service_sets_detailed', {'status': 'ok',
            'service_sets': [
                {'name': 'n', 'service_types': ['n'], 'tariffs': []},
            ]
        })
        self.api.validate_response('view_service_sets_detailed', {'status': 'ok',
            'service_sets': [
                {'name': 'n', 'service_types': ['n'], 'tariffs': []},
                {'name': 'm', 'service_types': ['n', 'm'], 'tariffs': ['t0']},
                {'name': 'l', 'service_types': [], 'tariffs': ['t0', 't1']},
            ]
        })

    def test_add_tariff(self):
        self.api.validate_request('add_tariff', {'login': 'l', 'password': 'p',
            'name': 'n', 'parent_tariff': None, 'service_set': 's', 'in_archive': False})
        self.api.validate_request('add_tariff', {'login': 'l', 'password': 'p',
            'name': 'n', 'parent_tariff': 'bt', 'service_set': 's', 'in_archive': False,})

    def test_modify_tariff(self):
        self.api.validate_request('modify_tariff', {'login': 'l', 'password': 'p',
            'name': 'n', 'new_name': 'nn'})
        self.api.validate_request('modify_tariff', {'login': 'l', 'password': 'p',
            'name': 'n', 'new_in_archive': True})
        self.api.validate_request('modify_tariff', {'login': 'l', 'password': 'p',
            'name': 'n', 'new_name': 'nn', 'new_in_archive': True})
        self.api.validate_request('modify_tariff', {'login': 'l', 'password': 'p',
            'name': 'n', 'new_name': 'nn', 'new_in_archive': True, 'new_parent_tariff': None})
        self.api.validate_request('modify_tariff', {'login': 'l', 'password': 'p',
            'name': 'n', 'new_name': 'nn', 'new_in_archive': True, 'new_parent_tariff': 't'})
        self.api.validate_request('modify_tariff', {'login': 'l', 'password': 'p',
            'name': 'n', 'new_name': 'nn', 'new_service_set': 's'})
        self.api.validate_request('modify_tariff', {'login': 'l', 'password': 'p', 'name': 'n'})
        self.validate_status_response('modify_tariff')
        self.api.validate_response('modify_tariff',
            {'status': 'error', 'category': 't', 'message': 'm'})

    def test_delete_tariff(self):
        self.api.validate_request('delete_tariff', {'login': 'l', 'password': 'p', 'name': 'приведи друга'})
        self.validate_status_response('delete_tariff')

    def test_get_tariff(self):
        self.api.validate_request('get_tariff',
            {'login': 'l', 'password': 'p', 'name': 'приведи друга'})
        self.api.validate_response('get_tariff', {'status': 'error', 'category': 't', 'message': 'h'})
        self.api.validate_response('get_tariff', {'status': 'ok', 'name': 'n', 'service_set': 's',
            'parent_tariff': 'n', 'tariffs_chain': ['n'], 'in_archive': False})
        self.api.validate_response('get_tariff', {'status': 'ok', 'name': 'n', 'service_set': 's',
            'parent_tariff': None, 'tariffs_chain': ['n', 't'], 'in_archive': True})

    def test_get_tariff_detailed(self):
        self.api.validate_request('get_tariff_detailed',
            {'login': 'l', 'password': 'p', 'name': 'приведи друга'})
        self.api.validate_response('get_tariff_detailed', {'status': 'error', 'category': 't', 'message': 'm'})
        self.api.validate_response('get_tariff_detailed', {'status': 'ok', 'name': 'n',
            'service_set': 's', 'tariffs_chain': ['n'], 'service_types': ['one', 'two'],
            'parent_tariff': 'pt', 'in_archive': False})
        self.api.validate_response('get_tariff_detailed', {'status': 'ok', 'name': 'n',
            'tariffs_chain': ['n', 't'], 'service_set': 's', 'service_types': [],
            'parent_tariff': None, 'in_archive': True})

    def test_save_draft_rule(self):
        self.api.validate_request('save_draft_rule', {'login': 'l', 'password': 'p', 'tariff': 't',
            'service_type': 's', 'rule': 'price = 10', 'enabled': True})
        self.validate_status_response('save_draft_rule')

    def test_make_draft_rules_actual(self):
        self.api.validate_request('make_draft_rules_actual', {'login': 'l', 'password': 'p', 'tariff': 't'})
        self.validate_status_response('make_draft_rules_actual')

    def test_modify_actual_rule(self):
        self.api.validate_request('modify_actual_rule', {'login': 'l', 'password': 'p', 'tariff': 't',
            'service_type': 's', 'new_enabled': False})
        self.validate_status_response('modify_actual_rule')

    def test_get_rule(self):
        self.api.validate_request('get_rule', {'login': 'l', 'password': 'p',
            'tariff': 'auto', 'service_type': 'ru', 'type': Rule.TYPE_ACTUAL})
        self.api.validate_request('get_rule', {'login': 'l', 'password': 'p',
            'tariff': 'auto', 'service_type': 'ru', 'type': Rule.TYPE_DRAFT})
        self.api.validate_response('get_rule',
            {'status': 'error', 'category': 't', 'message': 'm'})
        self.api.validate_response('get_rule', {'status': 'ok', 'tariff': 't',
            'service_type': 't', 'rule': 'r', 'type': Rule.TYPE_ACTUAL, 'enabled': True})
        self.api.validate_response('get_rule', {'status': 'ok', 'tariff': 't',
            'service_type': 't', 'rule': 'r', 'type': Rule.TYPE_DRAFT, 'enabled': False})

    def test_view_rules(self):
        self.api.validate_request('view_rules',
            {'login': 'l', 'password': 'p', 'tariff': 't'})
        self.api.validate_response('view_rules',
            {'status': 'error', 'category': 't', 'message': 'm'})
        self.api.validate_response('view_rules', {'status': 'ok', 'tariff': 't', 'rules': []})
        self.api.validate_response('view_rules', {'status': 'ok', 'tariff': 't',
            'rules': [
                {'service_type': 't', 'rule': 'r', 'type': Rule.TYPE_ACTUAL, 'enabled': True},
            ]
        })
        self.api.validate_response('view_rules', {'status': 'ok', 'tariff': 't',
            'rules': [
                {'service_type': 't', 'rule': 'r', 'type': Rule.TYPE_ACTUAL, 'enabled': False},
                {'service_type': 't', 'rule': 'r', 'type': Rule.TYPE_DRAFT, 'enabled': True},
            ]
        })

    def test_get_price(self):
        self.api.validate_request('get_price',
            {'login': 'l', 'password': 'p', 'tariff': 't', 'service_type': 's'})
        self.api.validate_request('get_price',
            {'login': 'l', 'password': 'p', 'tariff': 't', 'service_type': 's', 'context': {}})
        self.api.validate_request('get_price',
            {'login': 'l', 'password': 'p', 'tariff': 't', 'service_type': 's', 'context': {'a': 2}})
        self.api.validate_request('get_price',
            {'login': 'l', 'password': 'p', 'tariff': 't', 'service_type': 's', 'context': {'a': 1, 'b': 3}})

        self.api.validate_response('get_price',
            {'status': 'error', 'category': 'test', 'message': 'happens'})
        self.api.validate_response('get_price', {'status': 'ok', 'tariff': 'n', 'service_type': 's',
            'tariffs_chain': [], 'price': None, 'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
            'draft_tariffs_chain': ['m'], 'draft_price': None, 'draft_price_calculation': PRICE_CALC_PRICE_UNDEFINED,
            'context': {}})
        self.api.validate_response('get_price', {'status': 'ok', 'tariff': 'n', 'service_type': 's',
            'tariffs_chain': [], 'price': '1', 'price_calculation': PRICE_CALC_NORMAL,
            'draft_tariffs_chain': ['m'], 'draft_price': None, 'draft_price_calculation': PRICE_CALC_PRICE_UNDEFINED,
            'context': {}})
        self.api.validate_response('get_price', {'status': 'ok', 'tariff': 'n', 'service_type': 's',
            'tariffs_chain': [], 'price': '1', 'price_calculation': PRICE_CALC_NORMAL,
            'draft_tariffs_chain': ['m'], 'draft_price': '11', 'draft_price_calculation': PRICE_CALC_NORMAL,
            'context': {}})
        self.api.validate_response('get_price', {'status': 'ok', 'tariff': 'n', 'service_type': 's',
            'tariffs_chain': [], 'price': '1', 'price_calculation': PRICE_CALC_NORMAL,
            'draft_tariffs_chain': ['m'], 'draft_price': None, 'draft_price_calculation': PRICE_CALC_RULE_DISABLED,
            'context': {}})

    def test_view_prices(self):
        self.api.validate_request('view_prices',
            {'login': 'l', 'password': 'p', 'tariff': 't'})
        self.api.validate_response('view_prices',
            {'status': 'error', 'category': 't', 'message': 'm'})
        self.api.validate_response('view_prices', {'status': 'ok', 'tariff': 't', 'context': {},
            'prices': []})
        self.api.validate_response('view_prices', {'status': 'ok', 'tariff': 't', 'context': {'customer_id': 'c'},
            'prices': []})
        self.api.validate_response('view_prices', {'status': 'ok', 'tariff': 't', 'context': {'customer_id': 'c'},
            'prices': [
                {'service_type': 's',
                    'tariffs_chain': [], 'price': '1', 'price_calculation': PRICE_CALC_NORMAL,
                    'draft_tariffs_chain': ['m'], 'draft_price': None, 'draft_price_calculation': PRICE_CALC_RULE_DISABLED},
            ]})
        self.api.validate_response('view_prices', {'status': 'ok', 'tariff': 't', 'context': {'customer_id': 'c'},
            'prices': [
                {'service_type': 's',
                    'tariffs_chain': [], 'price': '1', 'price_calculation': PRICE_CALC_NORMAL,
                    'draft_tariffs_chain': ['m'], 'draft_price': None, 'draft_price_calculation': PRICE_CALC_RULE_DISABLED},
                {'service_type': 's',
                    'tariffs_chain': [], 'price': None, 'price_calculation': PRICE_CALC_RULE_DISABLED,
                    'draft_tariffs_chain': ['m'], 'draft_price': '1', 'draft_price_calculation': PRICE_CALC_NORMAL},
            ]})

    def test_view_tariffs(self):
        self.api.validate_request('view_tariffs',
            {'login': 'l', 'password': 'p'})
        self.api.validate_response('view_tariffs',
            {'status': 'error', 'category': 'test', 'message': 'happens'})
        self.api.validate_response('view_tariffs', {'status': 'ok', 'tariffs': []})
        self.api.validate_response('view_tariffs', {'status': 'ok',
            'tariffs': [
                {'name': 'n', 'service_set': 's', 'tariffs_chain': ['n'], 'in_archive': True,
                    'parent_tariff': None},
            ]
        })
        self.api.validate_response('view_tariffs', {'status': 'ok',
            'tariffs': [
                {'name': 'n', 'service_set': 's', 'tariffs_chain': ['n'], 'in_archive': False,
                    'parent_tariff': None},
                {'name': 'n', 'service_set': 's', 'tariffs_chain': ['n', 't'], 'in_archive': True,
                    'parent_tariff': 'pt'},
            ]
        })

    def test_view_detailed_tariffs(self):
        self.api.validate_request('view_detailed_tariffs',
            {'login': 'l', 'password': 'p'})
        self.api.validate_response('view_detailed_tariffs',
            {'status': 'error', 'category': 'test', 'message': 'happens'})
        self.api.validate_response('view_detailed_tariffs', {'status': 'ok', 'tariffs': []})
        self.api.validate_response('view_detailed_tariffs', {'status': 'ok',
            'tariffs': [
                {'name': 'n', 'service_set': 's', 'tariffs_chain': ['n'], 'in_archive': True,
                    'service_types': [], 'parent_tariff': 'pt'},
            ]
        })
        self.api.validate_response('view_detailed_tariffs', {'status': 'ok',
            'tariffs': [
                {'name': 'n', 'service_set': 's', 'tariffs_chain': ['n'], 'in_archive': False,
                    'service_types': ['a', 'b'], 'parent_tariff': 'pt'},
                {'name': 'n', 'service_set': 's', 'tariffs_chain': ['n', 't'], 'in_archive': True,
                    'service_types': [], 'parent_tariff': None},
            ]
        })


if __name__ == '__main__':
    unittest.main()
