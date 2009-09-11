import unittest

from helixcore.test.root_test import RootTestCase
from helixtariff.validator.validator import validate, ValidationError


class ValidatorTestCase(RootTestCase):
    def test_add_service_type(self):
        validate(
            'add_service_type', { 'name': 'register_ru' }
        )

    def test_add_service_type_invalid(self):
        self.assertRaises(ValidationError,
            validate, 'add_service_type', { 'name': 77 }
        )

    def test_modify_service_type(self):
        validate(
            'modify_service_type', { 'name': 'register_ru', 'new_name': 'register_RU' }
        )

    def test_modify_service_type_invalid(self):
        self.assertRaises(ValidationError,
            validate, 'modify_service_type', { 'name': 'chelios' }
        )


if __name__ == '__main__':
    unittest.main()
