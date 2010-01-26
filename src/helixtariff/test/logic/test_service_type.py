import unittest

from helixcore.server.exceptions import AuthError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action
from helixtariff.error import ServiceTypeUsed, ServiceTypeNotFound


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
        t_old = self.get_service_type(self.client.id, old_name)

        new_name = 'new' + old_name
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': old_name,
            'new_name': new_name
        }
        self.handle_action('modify_service_type', data)

        t_new = self.get_service_type(self.client.id, new_name)
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
        self.assertRaises(ServiceTypeNotFound, self.get_service_type,
            self.client.id, self.service_type_name)

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

    def test_view_empty_service_types(self):
        response = self.handle_action('view_service_types', {'login': self.test_client_login,
            'password': self.test_client_password})
        self.assertTrue('service_types' in response)
        self.assertEqual([], response['service_types'])

    def test_view_empty_service_types_detailed(self):
        response = self.handle_action('view_service_types_detailed', {'login': self.test_client_login,
            'password': self.test_client_password})
        self.assertTrue('service_types' in response)
        self.assertEqual([], response['service_types'])

    def test_view_service_types_detailed_without_service_set(self):
        self.add_service_types([self.service_type_name])
        response = self.handle_action('view_service_types_detailed', {'login': self.test_client_login,
            'password': self.test_client_password})
        expected_st_info = [{'service_sets': [], 'name': self.service_type_name}]
        self.assertTrue('service_types' in response)
        self.assertEqual(expected_st_info, response['service_types'])

    def test_view_service_types(self):
        types = ['one', 'two', 'three']
        self.add_service_types(types)
        response = self.handle_action('view_service_types', {'login': self.test_client_login,
            'password': self.test_client_password})
        self.assertTrue('service_types' in response)
        self.assertEqual(types, response['service_types'])

    def test_view_service_types_invalid(self):
        self.assertRaises(AuthError, handle_action, 'view_service_types', {'login': 'fake',
            'password': self.test_client_password})

    def test_view_service_types_detailed(self):
        types = ['one', 'two', 'three']
        self.add_service_types(types)
        ss_struct = {
            's0': types[1:],
            's1': [],
            's2': types,
        }
        st_struct = {}
        for ss_name, st_names in ss_struct.items():
            for t_name in st_names:
                if t_name not in st_struct:
                    st_struct[t_name] = set()
                st_struct[t_name].add(ss_name)

        for ss_name, st_names in ss_struct.items():
            self.add_service_sets([ss_name], st_names)
        response = self.handle_action('view_service_types_detailed', {'login': self.test_client_login,
            'password': self.test_client_password})
        self.assertEqual('ok', response['status'])
        service_types_info = response['service_types']
        for st_info in service_types_info:
            st_name = st_info['name']
            self.assertEqual(sorted(list(st_struct[st_name])), st_info['service_sets'])


if __name__ == '__main__':
    unittest.main()