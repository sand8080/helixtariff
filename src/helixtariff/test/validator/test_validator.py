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

    def validate_error_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'error', 'category': 't',
            'message': 'h', 'details': [{'f': 'v'}]})
        self.api.validate_response(action_name, {'status': 'error', 'category': 't',
            'message': 'h', 'details': [{}]})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'category': 'test'})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'category': 'test', 'message': 'm'})

    def validate_status_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'ok'})
        self.validate_error_response(action_name)

    def test_ping(self):
        a_name = 'ping'
        self.api.validate_request(a_name, {})
        self.validate_status_response(a_name)

    def test_add_client(self):
        a_name = 'add_client'
        self.api.validate_request(a_name, {'login': 'admin', 'password': 'crypted twice'})
        self.validate_status_response(a_name)
        self.assertRaises(ValidationError, self.api.validate_request, a_name, {'login': 'admin'})
        self.assertRaises(ValidationError, self.api.validate_request, a_name, {'password': 'admin'})
        self.assertRaises(ValidationError, self.api.validate_request, a_name, {})

    def test_modify_client(self):
        a_name = 'modify_client'
        self.api.validate_request(a_name, {'login': 'log', 'password': 'pi', 'new_login': 'new_log'})
        self.api.validate_request(a_name, {'login': 'log', 'password': 'pi', 'new_login': 'new_log', 'new_password': 'pw'})
        self.api.validate_request(a_name, {'login': 'log', 'password': 'pi'})
        self.validate_status_response(a_name)

#    def test_delete_client(self):
#        a_name = 'delete_client'
#        self.api.validate_request(a_name, {'login': 'log', 'password': 'pi'})
#        self.validate_status_response(a_name)

    def test_add_service_type(self):
        a_name = 'add_service_type'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 'register_ru'})
        self.validate_status_response(a_name)
        self.assertRaises(ValidationError,self.api.validate_request, a_name, {'login': 'l', 'password': 'p', 'name': 77})

    def test_modify_service_type(self):
        a_name = 'modify_service_type'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 'register_ru',
            'new_name': 'register_RU'})
        self.validate_status_response(a_name)
        self.assertRaises(ValidationError, self.api.validate_request, a_name, {'login': 'l', 'password': 'p',
            'name': 'cheli0s'})


    def test_view_service_types(self):
        a_name = 'view_service_types'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p'})
        self.api.validate_response(a_name, {'status': 'ok', 'service_types': []})
        self.api.validate_response(a_name, {'status': 'ok', 'service_types': ['one', 'two']})
        self.validate_error_response(a_name)

    def test_view_service_types_detailed(self):
        a_name = 'view_service_types_detailed'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p'})
        self.api.validate_response(a_name, {'status': 'ok', 'service_types': []})
        self.api.validate_response(a_name, {'status': 'ok', 'service_types': [
            {'name': 'n', 'service_sets': []},
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'service_types': [
            {'name': 'n', 'service_sets': []},
            {'name': 'm', 'service_sets': ['s0', 's1']},
        ]})
        self.validate_error_response(a_name)

    def test_delete_service_type(self):
        a_name = 'delete_service_type'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 'register_ru'})
        self.validate_status_response(a_name)

    def test_add_service_set(self):
        a_name = 'add_service_set'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'name': 'basic', 'service_types': []})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'name': 'basic', 'service_types': ['a', 'b', 'c']})
        self.validate_status_response(a_name)

    def test_modify_service_set(self):
        a_name = 'modify_service_set'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 's'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 's',
            'new_name': 'ns'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 's',
            'new_name': 'ns', 'new_service_types': ['1', '2']})
        self.validate_status_response(a_name)

    def test_delete_service_set(self):
        a_name = 'delete_service_set'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 's'})
        self.validate_status_response(a_name)

    def test_get_service_set(self):
        a_name = 'get_service_set'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 't'})
        self.api.validate_response(a_name, {'status': 'ok', 'name': 'n', 'service_types': []})
        self.api.validate_response(a_name, {'status': 'ok', 'name': 'n', 'service_types': ['n']})
        self.api.validate_response(a_name, {'status': 'ok', 'name': 'n', 'service_types': ['n', 'm']})
        self.validate_error_response(a_name)

    def test_get_service_set_detailed(self):
        a_name = 'get_service_set_detailed'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 't'})
        self.api.validate_response(a_name, {'status': 'ok', 'name': 'n',
            'service_types': [], 'tariffs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'name': 'n',
            'service_types': ['n'], 'tariffs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'name': 'n',
            'service_types': ['n', 'm'], 'tariffs': ['t0', 't1']})
        self.validate_error_response(a_name)

    def test_view_service_sets(self):
        a_name = 'view_service_sets'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p'})
        self.api.validate_response(a_name, {'status': 'ok', 'service_sets': []})
        self.api.validate_response(a_name, {'status': 'ok', 'service_sets': [
                {'name': 'n', 'service_types': ['n']},
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'service_sets': [
            {'name': 'n', 'service_types': ['n']},
            {'name': 'm', 'service_types': ['n', 'm']},
            {'name': 'l', 'service_types': []},
        ]})
        self.validate_error_response(a_name)

    def test_view_service_sets_detailed(self):
        a_name = 'view_service_sets_detailed'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p'})
        self.api.validate_response(a_name, {'status': 'ok', 'service_sets': []})
        self.api.validate_response(a_name, {'status': 'ok', 'service_sets': [
            {'name': 'n', 'service_types': ['n'], 'tariffs': []},
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'service_sets': [
            {'name': 'n', 'service_types': ['n'], 'tariffs': []},
            {'name': 'm', 'service_types': ['n', 'm'], 'tariffs': ['t0']},
            {'name': 'l', 'service_types': [], 'tariffs': ['t0', 't1']},
        ]})
        self.validate_error_response(a_name)

    def test_add_tariff(self):
        a_name = 'add_tariff'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 'n',
            'parent_tariff': None, 'service_set': 's', 'in_archive': False})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 'n',
            'parent_tariff': 'bt', 'service_set': 's', 'in_archive': False,})
        self.validate_status_response(a_name)

    def test_modify_tariff(self):
        a_name = 'modify_tariff'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'name': 'n', 'new_name': 'nn'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'name': 'n', 'new_in_archive': True})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'name': 'n', 'new_name': 'nn', 'new_in_archive': True})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'name': 'n', 'new_name': 'nn', 'new_in_archive': True, 'new_parent_tariff': None})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'name': 'n', 'new_name': 'nn', 'new_in_archive': True, 'new_parent_tariff': 't'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'name': 'n', 'new_name': 'nn', 'new_service_set': 's'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 'n'})
        self.validate_status_response(a_name)
        self.validate_error_response(a_name)

    def test_delete_tariff(self):
        a_name = 'delete_tariff'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 'n'})
        self.validate_status_response(a_name)

    def test_get_tariff(self):
        a_name = 'get_tariff'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 'n'})
        self.api.validate_response(a_name, {'status': 'ok', 'name': 'n', 'service_set': 's',
            'parent_tariff': 'n', 'tariffs_chain': ['n'], 'in_archive': False})
        self.api.validate_response(a_name, {'status': 'ok', 'name': 'n', 'service_set': 's',
            'parent_tariff': None, 'tariffs_chain': ['n', 't'], 'in_archive': True})
        self.validate_error_response(a_name)

    def test_get_tariff_detailed(self):
        a_name = 'get_tariff_detailed'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'name': 'n'})
        self.api.validate_response(a_name, {'status': 'ok', 'name': 'n',
            'service_set': 's', 'tariffs_chain': ['n'], 'service_types': ['one', 'two'],
            'parent_tariff': 'pt', 'in_archive': False})
        self.api.validate_response(a_name, {'status': 'ok', 'name': 'n',
            'tariffs_chain': ['n', 't'], 'service_set': 's', 'service_types': [],
            'parent_tariff': None, 'in_archive': True})
        self.validate_error_response(a_name)

    def test_view_tariffs(self):
        a_name = 'view_tariffs'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p'})
        self.api.validate_response(a_name, {'status': 'ok', 'tariffs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'tariffs': [
            {'name': 'n', 'service_set': 's', 'tariffs_chain': ['n'], 'in_archive': True, 'parent_tariff': None},
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'tariffs': [
            {'name': 'n', 'service_set': 's', 'tariffs_chain': ['n'], 'in_archive': False, 'parent_tariff': None},
            {'name': 'n', 'service_set': 's', 'tariffs_chain': ['n', 't'], 'in_archive': True, 'parent_tariff': 'pt'},
        ]})
        self.validate_error_response(a_name)

    def test_view_tariffs_detailed(self):
        a_name = 'view_tariffs_detailed'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p'})
        self.api.validate_response(a_name, {'status': 'ok', 'tariffs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'tariffs': [
            {'name': 'n', 'service_set': 's', 'tariffs_chain': ['n'], 'in_archive': True,
                'service_types': [], 'parent_tariff': 'pt'},
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'tariffs': [
            {'name': 'n', 'service_set': 's', 'tariffs_chain': ['n'], 'in_archive': False,
                'service_types': ['a', 'b'], 'parent_tariff': 'pt'},
            {'name': 'n', 'service_set': 's', 'tariffs_chain': ['n', 't'], 'in_archive': True,
                'service_types': [], 'parent_tariff': None},
        ]})
        self.validate_error_response(a_name)

    def test_save_draft_rule(self):
        a_name = 'save_draft_rule'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'tariff': 't',
            'service_type': 's', 'rule': 'price = 10', 'enabled': True})
        self.validate_status_response(a_name)

    def test_make_draft_rules_actual(self):
        a_name = 'make_draft_rules_actual'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'tariff': 't'})
        self.validate_status_response(a_name)

    def test_modify_actual_rule(self):
        a_name = 'modify_actual_rule'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'tariff': 't',
            'service_type': 's', 'new_enabled': False})
        self.validate_status_response(a_name)

    def test_get_rule(self):
        a_name = 'get_rule'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'tariff': 'auto', 'service_type': 'ru', 'type': Rule.TYPE_ACTUAL})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'tariff': 'auto', 'service_type': 'ru', 'type': Rule.TYPE_DRAFT})
        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 't',
            'service_type': 't', 'rule': 'r', 'type': Rule.TYPE_ACTUAL, 'enabled': True})
        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 't',
            'service_type': 't', 'rule': 'r', 'type': Rule.TYPE_DRAFT, 'enabled': False})
        self.validate_error_response(a_name)

    def test_view_rules(self):
        a_name = 'view_rules'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'tariff': 't'})
        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 't', 'rules': []})
        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 't', 'rules': [
            {'service_type': 't', 'rule': 'r', 'type': Rule.TYPE_ACTUAL, 'enabled': True},
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 't', 'rules': [
            {'service_type': 't', 'rule': 'r', 'type': Rule.TYPE_ACTUAL, 'enabled': False},
            {'service_type': 't', 'rule': 'r', 'type': Rule.TYPE_DRAFT, 'enabled': True},
        ]})
        self.validate_error_response(a_name)

    def test_get_price(self):
        a_name = 'get_price'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'tariff': 't', 'service_type': 's'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'tariff': 't', 'service_type': 's', 'context': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'tariff': 't', 'service_type': 's', 'context': {'a': 2}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'tariff': 't', 'service_type': 's', 'context': {'a': 1, 'b': 3}})

        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 'n', 'service_type': 's',
            'tariffs_chain': [], 'price': None, 'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
            'draft_tariffs_chain': ['m'], 'draft_price': None, 'draft_price_calculation': PRICE_CALC_PRICE_UNDEFINED,
            'context': {}})
        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 'n', 'service_type': 's',
            'tariffs_chain': [], 'price': '1', 'price_calculation': PRICE_CALC_NORMAL,
            'draft_tariffs_chain': ['m'], 'draft_price': None, 'draft_price_calculation': PRICE_CALC_PRICE_UNDEFINED,
            'context': {}})
        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 'n', 'service_type': 's',
            'tariffs_chain': [], 'price': '1', 'price_calculation': PRICE_CALC_NORMAL,
            'draft_tariffs_chain': ['m'], 'draft_price': '11', 'draft_price_calculation': PRICE_CALC_NORMAL,
            'context': {}})
        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 'n', 'service_type': 's',
            'tariffs_chain': [], 'price': '1', 'price_calculation': PRICE_CALC_NORMAL,
            'draft_tariffs_chain': ['m'], 'draft_price': None, 'draft_price_calculation': PRICE_CALC_RULE_DISABLED,
            'context': {}})
        self.validate_error_response(a_name)

    def test_view_prices(self):
        a_name = 'view_prices'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'tariff': 't'})
        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 't', 'context': {},
            'prices': []})
        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 't',
            'context': {'customer_id': 'c'}, 'prices': []})
        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 't', 'context': {'customer_id': 'c'},
            'prices': [
                {'service_type': 's',
                    'tariffs_chain': [], 'price': '1', 'price_calculation': PRICE_CALC_NORMAL,
                    'draft_tariffs_chain': ['m'], 'draft_price': None, 'draft_price_calculation': PRICE_CALC_RULE_DISABLED},
            ]})
        self.api.validate_response(a_name, {'status': 'ok', 'tariff': 't', 'context': {'customer_id': 'c'},
            'prices': [
                {'service_type': 's',
                    'tariffs_chain': [], 'price': '1', 'price_calculation': PRICE_CALC_NORMAL,
                    'draft_tariffs_chain': ['m'], 'draft_price': None, 'draft_price_calculation': PRICE_CALC_RULE_DISABLED},
                {'service_type': 's',
                    'tariffs_chain': [], 'price': None, 'price_calculation': PRICE_CALC_RULE_DISABLED,
                    'draft_tariffs_chain': ['m'], 'draft_price': '1', 'draft_price_calculation': PRICE_CALC_NORMAL},
            ]})
        self.validate_error_response(a_name)


if __name__ == '__main__':
    unittest.main()
