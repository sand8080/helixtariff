import unittest

from helixcore.server.errors import RequestProcessingError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.domain.security import encrypt_password
from helixtariff.error import OperatorNotFound


class OperatorTestCase(ServiceTestCase):
    def test_add_billing_manager(self):
        self.add_operator('a', 'b', custom_operator_info='jah')
        self.assertRaises(RequestProcessingError, self.add_operator, 'a', 'b')

    def test_modify_billing_manager(self):
        l_old = 'a'
        p_old = 'p'
        self.add_operator(l_old, p_old)
        operator_old = self.get_operator_by_login(l_old)

        login = 's'
        data = {
            'login': l_old,
            'password': p_old,
            'new_login': login,
        }
        self.handle_action('modify_operator', data)
        self.assertRaises(OperatorNotFound, self.get_operator_by_login, l_old)
        operator = self.get_operator_by_login(login)
        self.assertEqual(operator_old.id, operator.id)
        self.assertEqual(login, operator.login)

        password = 'yahoo'
        data = {
            'login': login,
            'password': p_old,
            'new_password': password,
        }
        self.handle_action('modify_operator', data)
        operator = self.get_operator_by_login(login)
        self.assertEqual(operator_old.id, operator.id)
        self.assertEqual(encrypt_password(password), operator.password)

        l_other = 'b'
        p_other = 'z'
        self.add_operator(l_other, p_other)
        data = {
            'login': login,
            'password': password,
            'new_login': l_other,
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'modify_operator', data)

    def test_auth_error(self):
        data = {
            'login': self.test_login,
            'password': 'fake %s' % self.test_password,
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'modify_operator', data)


if __name__ == '__main__':
    unittest.main()