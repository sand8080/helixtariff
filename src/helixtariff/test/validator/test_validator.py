# -*- coding: utf-8 -*-
import unittest

from helixcore.test.root_test import RootTestCase
from helixtariff.validator.validator import validate, ValidationError


class ValidatorTestCase(RootTestCase):
    def test_add_client(self):
        validate('add_client', {'login': 'admin', 'password': 'crypted twice'})

    def test_add_client_invalid(self):
        self.assertRaises(ValidationError, validate, 'add_client', {'login': 'admin'})
        self.assertRaises(ValidationError, validate, 'add_client', {'password': 'admin'})
        self.assertRaises(ValidationError, validate, 'add_client', {})

    def test_modify_client(self):
        validate('modify_client', {'login': 'log', 'password': 'pi', 'new_login': 'new_log'})
        validate('modify_client', {'login': 'log', 'password': 'pi', 'new_login': 'new_log', 'new_password': 'pw'})
        validate('modify_client', {'login': 'log', 'password': 'pi'})

    def test_add_service_type(self):
        validate('add_service_type', {'login': 'l', 'password': 'p', 'name': 'register_ru'})

    def test_add_service_type_invalid(self):
        self.assertRaises(ValidationError,validate, 'add_service_type', {'login': 'l', 'password': 'p', 'name': 77})

    def test_modify_service_type(self):
        validate('modify_service_type', {'login': 'l', 'password': 'p', 'name': 'register_ru', 'new_name': 'register_RU'})

    def test_modify_service_type_invalid(self):
        self.assertRaises(ValidationError, validate, 'modify_service_type', {'login': 'l', 'password': 'p', 'name': 'cheli0s'})

    def test_delete_service_type(self):
        validate('delete_service_type', {'login': 'l', 'password': 'p', 'name': 'register_ru'})

    def test_add_service_set_descr(self):
        validate('add_service_set_descr', {'login': 'l', 'password': 'p', 'name': 'basic'})

    def test_modify_service_descr(self):
        validate('modify_service_set_descr', {'login': 'l', 'password': 'p', 'name': 'basic', 'new_name': 'restricted'})

    def test_delete_service_descr(self):
        validate('delete_service_set_descr', {'login': 'l', 'password': 'p', 'name': 'basic'})

    def test_add_to_service_set(self):
        validate(
            'add_to_service_set',
            {
                'login': 'l',
                'password': 'p',
                'name': 'basic',
                'types': ['ssl123', 'sslsuper0']
            }
        )

    def test_delete_from_service_set(self):
        validate(
            'delete_from_service_set',
            {
                'login': 'l',
                'password': 'p',
                'name': 'basic',
                'types': ['ssl123', 'sslsuper0']
            }
        )

    def test_delete_service_set(self):
        validate('delete_service_set', {'login': 'l', 'password': 'p', 'name': 'basic'})

    def test_add_tariff(self):
        validate(
            'add_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга',
                'service_set_descr_name': 'exotic',
                'in_archive': False,
            }
        )

    def test_modify_tariff(self):
        validate(
            'modify_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга',
                'new_name': 'для блондинок'
            }
        )
        validate(
            'modify_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга',
                'new_in_archive': True
            }
        )
        validate(
            'modify_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга',
                'new_name': 'для блондинок',
                'new_in_archive': True
            }
        )
        validate(
            'modify_tariff',
            {
                'login': 'l',
                'password': 'p',
                'name': 'приведи друга'
            }
        )

    def test_delete_tariff(self):
        validate('delete_tariff', {'login': 'l', 'password': 'p', 'name': 'приведи друга'})

    def test_add_rule(self):
        validate(
            'add_rule',
            {
                'login': 'l',
                'password': 'p',
                'tariff_name': 'auto',
                'service_type_name': 'ru',
                'rule': 'price = 10'
            }
        )

    def test_modify_rule(self):
        validate(
            'modify_rule',
            {
                'login': 'l',
                'password': 'p',
                'tariff_name': 'auto',
                'service_type_name': 'ru',
                'new_rule': 'price = 20'
            }
        )
        self.assertRaises(ValidationError, validate, 'modify_rule', {'tariff_name': 'auto', 'service_type_name': 'ru'})

    def test_delete_rule(self):
        validate(
            'delete_rule',
            {
                'login': 'l',
                'password': 'p',
                'tariff_name': 'auto',
                'service_type_name': 'ru'
            }
        )


if __name__ == '__main__':
    unittest.main()
