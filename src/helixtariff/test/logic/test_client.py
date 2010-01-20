import unittest

from helixcore.db.wrapper import EmptyResultSetError, ObjectAlreadyExists
from helixcore.server.exceptions import AuthError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class ClientTestCase(ServiceTestCase):
    def test_add_client(self):
        self.add_client('john', 'milk and soda')

    def test_add_client_invalid(self):
        self.add_client('john', 'milk and soda')
        self.assertRaises(ObjectAlreadyExists, self.add_client, 'john', 'milk and cola')

    def test_modify_client(self):
        login_old = 'john'
        password_old = 'milk and soda'
        self.add_client(login_old, password_old)
        c_old = self.get_client_by_login(login_old)

        login_new = 'silver'
        data = {
            'login': login_old,
            'password': password_old,
            'new_login': login_new
        }
        handle_action('modify_client', data)
        self.assertRaises(EmptyResultSetError, self.get_client_by_login, c_old.login)
        c_new_0 = self.get_client_by_login(login_new)
        self.assertEqual(c_old.id, c_new_0.id)
        self.assertEqual(login_new, c_new_0.login)

        password_new = 'yahoo'
        data = {
            'login': login_new,
            'password': password_old,
            'new_login': c_old.login,
            'new_password': password_new
        }
        handle_action('modify_client', data)
        self.assertRaises(EmptyResultSetError, self.get_client_by_login, c_new_0.login)
        c_new_1 = self.get_client_by_login(c_old.login)
        self.assertEqual(c_old.id, c_new_1.id)
        self.assertEqual(c_old.login, c_new_1.login)
        self.assertNotEqual(c_new_0.password, c_new_1.password)

        data = {
            'login': c_new_1.login,
            'password': password_new
        }
        handle_action('modify_client', data)
        c_new_2 = self.get_client_by_login(c_new_1.login)
        self.assertEqual(c_new_1.id, c_new_2.id)
        self.assertEqual(c_new_1.login, c_new_2.login)
        self.assertEqual(c_new_1.password, c_new_2.password)

    def test_access_dinied(self):
        login_old = 'john'
        password = 'milk and soda'
        self.add_client(login_old, password)
        data = {'login': login_old, 'password': password + ' ', 'new_login': 'silver'}
        self.assertRaises(AuthError, handle_action, 'modify_client', data)

    def test_delete_client(self):
        login = 'zimorodok'
        self.add_client(login, '')
        handle_action('delete_client', {'login': login, 'password': ''})
        self.assertRaises(EmptyResultSetError, self.get_client_by_login, login)


if __name__ == '__main__':
    unittest.main()