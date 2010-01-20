from helixtariff.error import ServiceTypeUsed
import unittest

from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.exceptions import AuthError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class ServiceTypeTestCase(ServiceTestCase):
    service_type_name = 'registration ru'

    def setUp(self):
        super(ServiceTypeTestCase, self).setUp()
        self.client = self.get_root_client()

    def test_add_service_type(self):
        self.add_service_types([self.service_type_name])

    def test_modify_service_type(self):
        self.add_service_types([self.service_type_name])
        old_name = self.service_type_name
        t_old = self.get_service_type_by_name(self.client.id, old_name)

        new_name = 'new' + old_name
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': old_name,
            'new_name': new_name
        }
        handle_action('modify_service_type', data)

        t_new = self.get_service_type_by_name(self.client.id, new_name)
        self.assertEqual(t_old.id, t_new.id)
        self.assertEquals(t_new.name, new_name)

    def test_delete_service_type(self):
        self.add_service_types([self.service_type_name])
        handle_action(
            'delete_service_type',
            {
                'login': self.test_client_login,
                'password': self.test_client_password,
                'name': self.service_type_name,
            }
        )
        self.assertRaises(EmptyResultSetError, self.get_service_type_by_name, self.client.id, self.service_type_name)

    def test_delete_used_service_type(self):
        service_types_names = [self.service_type_name]
        self.add_service_types(service_types_names)
        service_sets_names = ['s0']
        self.add_service_sets(service_sets_names, service_types_names)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.service_type_name,
        }
        self.assertRaises(ServiceTypeUsed, handle_action, 'delete_service_type', data)

    def test_get_empty_service_types(self):
        response = handle_action('view_service_types', {'login': self.test_client_login,
            'password': self.test_client_password})
        self.assertTrue('service_types' in response)
        self.assertEqual([], response['service_types'])

    def test_view_service_types(self):
        types = ['one', 'two', 'three']
        self.add_service_types(types)
        response = handle_action('view_service_types', {'login': self.test_client_login,
            'password': self.test_client_password})
        self.assertTrue('service_types' in response)
        self.assertEqual(types, response['service_types'])

    def test_get_service_types_invalid(self):
        self.assertRaises(AuthError, handle_action, 'view_service_types', {'login': 'fake',
            'password': self.test_client_password})


if __name__ == '__main__':
    unittest.main()