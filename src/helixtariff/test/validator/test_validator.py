# -*- coding: utf-8 -*-
import unittest

from helixcore.test.root_test import RootTestCase
from helixcore.server.exceptions import ValidationError
from helixcore.server.api import Api

from helixtariff.validator.validator import protocol


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

    def test_get_service_types(self):
        self.api.validate_request('get_service_types', {'login': 'l', 'password': 'p'})
        self.api.validate_response('get_service_types', {'status': 'ok', 'types': []})
        self.api.validate_response('get_service_types', {'status': 'ok', 'types': ['one', 'two']})
        self.api.validate_response('get_service_types', {'status': 'error', 'category': 'test', 'message': 'happens'})

    def test_modify_service_type_invalid(self):
        self.assertRaises(ValidationError, self.api.validate_request, 'modify_service_type', {'login': 'l', 'password': 'p', 'name': 'cheli0s'})

    def test_delete_service_type(self):
        self.api.validate_request('delete_service_type', {'login': 'l', 'password': 'p', 'name': 'register_ru'})
        self.validate_status_response('delete_service_type')

    def test_add_service_set(self):
        self.api.validate_request('add_service_set', {'login': 'l', 'password': 'p', 'name': 'basic'})
        self.validate_status_response('add_service_set')

    def test_rename_service_set(self):
        self.api.validate_request('rename_service_set', {'login': 'l', 'password': 'p',
            'name': 'basic', 'new_name': 'restricted'})
        self.validate_status_response('rename_service_set')

    def test_delete_service_set(self):
        self.api.validate_request('delete_service_set', {'login': 'l', 'password': 'p', 'name': 'basic'})
        self.validate_status_response('delete_service_set')

    def test_add_to_service_set(self):
        self.api.validate_request(
            'add_to_service_set',
            {
                'login': 'l',
                'password': 'p',
                'name': 'basic',
                'types': ['ssl123', 'sslsuper0']
            }
        )
        self.validate_status_response('add_to_service_set')

    def test_delete_from_service_set(self):
        self.api.validate_request(
            'delete_from_service_set',
            {
                'login': 'l',
                'password': 'p',
                'name': 'basic',
                'types': ['ssl123', 'sslsuper0']
            }
        )
        self.validate_status_response('delete_from_service_set')

    def test_add_tariff(self):
        self.api.validate_request(
            'add_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга',
                'parent_tariff': None,
                'service_set': 'exotic',
                'in_archive': False,
            }
        )
        self.api.validate_request(
            'add_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга',
                'parent_tariff': 'basic exotic',
                'service_set': 'exotic',
                'in_archive': False,
            }
        )
        self.validate_status_response('add_tariff')

    def test_modify_tariff(self):
        self.api.validate_request(
            'modify_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга',
                'new_name': 'для блондинок'
            }
        )
        self.api.validate_request(
            'modify_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга',
                'new_in_archive': True
            }
        )
        self.api.validate_request(
            'modify_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга',
                'new_name': 'для блондинок',
                'new_in_archive': True
            }
        )
        self.api.validate_request(
            'modify_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга',
                'new_name': 'для блондинок',
                'new_in_archive': True,
                'new_parent_tariff': None
            }
        )
        self.api.validate_request(
            'modify_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга',
                'new_name': 'для блондинок',
                'new_in_archive': True,
                'new_parent_tariff': 'первый целевой'
            }
        )
        self.api.validate_request(
            'modify_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга'
            }
        )
        self.validate_status_response('modify_tariff')

    def test_delete_tariff(self):
        self.api.validate_request('delete_tariff', {'login': 'l', 'password': 'p', 'name': 'приведи друга'})
        self.validate_status_response('delete_tariff')

    def test_get_tariff(self):
        self.api.validate_request('get_tariff',
            {'login': 'l', 'password': 'p', 'name': 'приведи друга'})
        self.api.validate_response('get_tariff', {'status': 'error', 'category': 't', 'message': 'h'})
        self.api.validate_response('get_tariff', {'status': 'ok', 'tariff':
            {'name': 'n', 'service_set': 's', 'parent_tariff': None, 'in_archive': False}})
        self.api.validate_response('get_tariff', {'status': 'ok', 'tariff':
            {'name': 'n', 'service_set': 's', 'parent_tariff': 'p', 'in_archive': True}})

    def test_get_tariff_detailed(self):
        self.api.validate_request('get_tariff_detailed',
            {'login': 'l', 'password': 'p', 'name': 'приведи друга'})
        self.api.validate_response('get_tariff_detailed', {'status': 'error', 'category': 't', 'message': 'm'})
        self.api.validate_response('get_tariff_detailed', {'status': 'ok', 'tariff':
            {'name': 'n', 'service_set': 's', 'parent_tariff': None, 'types': ['one', 'two'], 'in_archive': False}})
        self.api.validate_response('get_tariff_detailed', {'status': 'ok', 'tariff':
            {'name': 'n', 'parent_tariff': 'p', 'service_set': 's', 'types': [], 'in_archive': True}})

    def test_add_rule(self):
        self.api.validate_request(
            'add_rule',
            {
                'login': 'l',
                'password': 'p',
                'tariff': 'auto',
                'service_type': 'ru',
                'rule': 'price = 10'
            }
        )
        self.validate_status_response('add_rule')

    def test_modify_rule(self):
        self.api.validate_request(
            'modify_rule',
            {
                'login': 'l',
                'password': 'p',
                'tariff': 'auto',
                'service_type': 'ru',
                'new_rule': 'price = 20'
            }
        )
        self.validate_status_response('modify_rule')
        self.assertRaises(ValidationError, self.api.validate_request,
            'modify_rule', {'tariff': 'auto', 'service_type': 'ru'})

    def test_delete_rule(self):
        self.api.validate_request(
            'delete_rule',
            {
                'login': 'l',
                'password': 'p',
                'tariff': 'auto',
                'service_type': 'ru'
            }
        )
        self.validate_status_response('delete_rule')

    def test_get_domain_service_price(self):
        self.api.validate_request('get_domain_service_price',
            {'login': 'l', 'password': 'p', 'tariff': 't', 'service_type': 's'})
        self.api.validate_request('get_domain_service_price',
            {'login': 'l', 'password': 'p', 'tariff': 't', 'service_type': 's', 'period': 3})
        self.api.validate_request('get_domain_service_price',
            {'login': 'l', 'password': 'p', 'tariff': 't', 'service_type': 's', 'period': 3, 'customer_id': 'c'})

        self.api.validate_response('get_domain_service_price',
            {'status': 'error', 'category': 'test', 'message': 'happens'})
        self.api.validate_response('get_domain_service_price', {'status': 'ok', 'tariff': 'n',
            'tariffs_chain': [], 'service_type': 's', 'price': '10.09'})
        self.api.validate_response('get_domain_service_price', {'status': 'ok', 'tariff': 'n',
            'tariffs_chain': ['m'], 'service_type': 's', 'price': '10.09', 'period': 1})
        self.api.validate_response('get_domain_service_price', {'status': 'ok', 'tariff': 'n',
            'tariffs_chain': ['m', 'n'], 'service_type': 's', 'price': '10.09', 'period': 1, 'customer_id': 'l'})

    def test_get_domain_service_price_invalid(self):
        self.assertRaises(ValidationError, self.api.validate_request, 'get_domain_service_price',
            {'login': 'l', 'tariff_name': 't', 'service_type_name': 's', 'period': 'f'})

    def test_view_service_set(self):
        self.api.validate_request('view_service_set',
            {'login': 'l', 'password': 'p', 'name': 't'})
        self.api.validate_response('view_service_set',
            {'status': 'error', 'category': 'test', 'message': 'happens'})
        self.api.validate_response('view_service_set', {'status': 'ok', 'name': 'n', 'types': []})
        self.api.validate_response('view_service_set', {'status': 'ok', 'name': 'n',
            'types': ['n']})
        self.api.validate_response('view_service_set', {'status': 'ok', 'name': 'n',
            'types': ['n', 'm']})

    def test_view_service_sets(self):
        self.api.validate_request('view_service_sets',
            {'login': 'l', 'password': 'p'})
        self.api.validate_response('view_service_sets',
            {'status': 'error', 'category': 'test', 'message': 'happens'})
        self.api.validate_response('view_service_sets', {'status': 'ok', 'service_sets': []})
        self.api.validate_response('view_service_sets', {'status': 'ok',
            'service_sets': [
                {'name': 'n', 'types': ['n']},
            ]
        })
        self.api.validate_response('view_service_sets', {'status': 'ok',
            'service_sets': [
                {'name': 'n', 'types': ['n']},
                {'name': 'm', 'types': ['n', 'm']},
                {'name': 'l', 'types': []},
            ]
        })

    def test_view_tariffs(self):
        self.api.validate_request('view_tariffs',
            {'login': 'l', 'password': 'p'})
        self.api.validate_response('view_tariffs',
            {'status': 'error', 'category': 'test', 'message': 'happens'})
        self.api.validate_response('view_tariffs', {'status': 'ok', 'tariffs': []})
        self.api.validate_response('view_tariffs', {'status': 'ok',
            'tariffs': [
                {'name': 'n', 'service_set': 's', 'parent_tariff': None, 'in_archive': True},
            ]
        })
        self.api.validate_response('view_tariffs', {'status': 'ok',
            'tariffs': [
                {'name': 'n', 'service_set': 's', 'parent_tariff': None, 'in_archive': False},
                {'name': 'n', 'service_set': 's', 'parent_tariff': 't', 'in_archive': True},
            ]
        })


if __name__ == '__main__':
    unittest.main()
