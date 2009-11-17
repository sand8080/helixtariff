import unittest

from helixcore.db.wrapper import EmptyResultSetError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class ServiceTypeTestCase(ServiceTestCase):
    descr_name = 'registration ru'

    def setUp(self):
        super(ServiceTypeTestCase, self).setUp()
        self.client = self.get_root_client()

    def test_add_service_type(self):
        self.add_types([self.descr_name])

    def test_modify_service_type(self):
        self.test_add_service_type()
        old_name = self.descr_name
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
        self.test_add_service_type()
        handle_action(
            'delete_service_type',
            {
                'login': self.test_client_login,
                'password': self.test_client_password,
                'name': self.descr_name,
            }
        )
        self.assertRaises(EmptyResultSetError, self.get_service_type_by_name, self.client.id, self.descr_name)

    def test_get_service_types(self):
        types = ['one', 'two', 'three']
        self.add_types(types)
        result = handle_action('get_service_types', {'login': self.test_client_login,})
        self.assertTrue('types' in result)
        self.assertEqual(types, result['types'])

    def test_get_service_types_invalid(self):
        self.assertRaises(EmptyResultSetError, handle_action, 'get_service_types', {'login': 'fake'})


if __name__ == '__main__':
    unittest.main()