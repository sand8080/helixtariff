# -*- coding: utf-8 -*-
import unittest

from helixcore.test.root_test import RootTestCase
from helixtariff.validator.validator import validate, ValidationError


class ValidatorTestCase(RootTestCase):
    def test_add_service_type(self):
        validate('add_service_type', {'name': 'register_ru'})

    def test_add_service_type_invalid(self):
        self.assertRaises(ValidationError,validate, 'add_service_type', {'name': 77})

    def test_modify_service_type(self):
        validate('modify_service_type', {'name': 'register_ru', 'new_name': 'register_RU'})

    def test_modify_service_type_invalid(self):
        self.assertRaises(ValidationError,validate, 'modify_service_type', {'name': 'cheli0s'})

    def test_delete_service_type(self):
        validate('delete_service_type', {'name': 'register_ru'})

    def test_add_service_set_descr(self):
        validate('add_service_set_descr', {'name': 'basic'})

    def test_modify_service_descr(self):
        validate('modify_service_set_descr', {'name': 'basic', 'new_name': 'restricted'})

    def test_delete_service_descr(self):
        validate('delete_service_set_descr', {'name': 'basic'})

    def test_add_to_service_set(self):
        validate('add_to_service_set', {'name': 'basic', 'types': ['ssl123', 'sslsuper0']})

    def test_delete_from_service_set(self):
        validate('delete_from_service_set', {'name': 'basic', 'types': ['ssl123', 'sslsuper0']})

    def test_delete_service_set(self):
        validate('delete_service_set', {'name': 'basic'})

    def test_add_tariff(self):
        validate(
            'add_tariff',
            {
                'client_id': 'coyote_45',
                'name': 'приведи друга',
                'service_set_descr_name': 'exotic',
                'in_archive': False,
            }
        )

    def test_modify_tariff(self):
        validate(
            'modify_tariff',
            {'client_id': 'coyote_45', 'name': 'приведи друга', 'new_name': 'для блондинок'}
        )
        validate(
            'modify_tariff',
            {'client_id': 'coyote_45', 'name': 'приведи друга', 'new_in_archive': True}
        )
        validate(
            'modify_tariff',
            {'client_id': 'coyote_45', 'name': 'приведи друга', 'new_name': 'для блондинок', 'new_in_archive': True}
        )
        validate('modify_tariff', {'client_id': 'coyote_45', 'name': 'приведи друга'})
        validate('modify_tariff', {'name': 'приведи друга', 'client_id': 'coyote_45'})

    def test_delete_tariff(self):
        validate('delete_tariff', {'client_id': 'coyote_45', 'name': 'приведи друга'})

    def test_add_rule(self):
        validate(
            'add_rule',
            {
                'client_id': 'coyote client 34',
                'tariff_name': 'automatic',
                'service_type_name': 'регистрация ru',
                'rule': 'price = 10'
            }
        )



if __name__ == '__main__':
    unittest.main()
