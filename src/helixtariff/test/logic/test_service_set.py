from helixtariff.error import ServiceTypeNotFound
import unittest

from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.exceptions import DataIntegrityError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class ServiceSetTestCase(ServiceTestCase):
    service_sets = ['automatic', 'exotic', 'full pack', 'manual']
    service_types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn', 'register dj', 'prolong dj']

    def setUp(self):
        super(ServiceSetTestCase, self).setUp()
        self.add_service_sets(self.service_sets)
        self.add_types(self.service_types_names)

    def test_add_service_sets(self):
        pass

    def test_rename_service_set(self):
        name = self.service_sets[0]
        client = self.get_client_by_login(self.test_client_login)
        s_old = self.get_service_set_by_name(client.id, name)

        new_name = 'new' + name
        data = {
            'login': client.login,
            'password': self.test_client_password,
            'name': name,
            'new_name': new_name
        }
        handle_action('rename_service_set', data)

        s_new = self.get_service_set_by_name(client.id, new_name)
        self.assertEqual(s_old.id, s_new.id)
        self.assertEquals(s_new.name, new_name)

    def test_delete_service_set(self):
        name = self.service_sets[0]
        client = self.get_client_by_login(self.test_client_login)
        data = {
            'login': client.login,
            'password': self.test_client_password,
            'name': name
        }
        handle_action('delete_service_set', data)
        self.assertRaises(EmptyResultSetError, self.get_service_set_by_name, client.id, name)

    def test_delete_nonempty_service_set_failure(self):
        name = self.service_sets[0]
        types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
        self.add_to_service_set(name, types_names)
        self.assertRaises(DataIntegrityError, handle_action,
            'delete_service_set',
            {
                'login': self.test_client_login,
                'password': self.test_client_password,
                'name': name
            }
        )

    def test_add_to_service_set(self):
        self.add_to_service_set('automatic', self.service_types_names)
        self.add_to_service_set('automatic', [self.service_types_names[0]])
        self.add_to_service_set('automatic', [self.service_types_names[0], self.service_types_names[0]])
        self.assertRaises(ServiceTypeNotFound, self.add_to_service_set,
            'automatic', ['register fake', 'register fake'])
        self.assertRaises(ServiceTypeNotFound, self.add_to_service_set,
            'automatic', ['register yo'])

    def test_delete_from_service_set(self):
        service_set_name = self.service_sets[0]
        self.add_to_service_set(service_set_name, self.service_types_names)
        self.delete_from_service_set(service_set_name, [])
        self.delete_from_service_set(service_set_name, ['fake'])
        self.delete_from_service_set(service_set_name, ['fake', 'fake'])
        self.delete_from_service_set(service_set_name, self.service_types_names[1:])
        self.delete_from_service_set(service_set_name, self.service_types_names)

    def test_view_service_set(self):
        service_set_name = self.service_sets[0]
        self.add_to_service_set(service_set_name, self.service_types_names)
        result = handle_action('view_service_set', {'login': self.test_client_login,
            'password': self.test_client_password, 'name': service_set_name,})
        self.assertEqual('ok', result['status'])
        self.assertEqual(service_set_name, result['name'])
        self.assertEquals(sorted(self.service_types_names), sorted(result['types']))

    def test_view_service_sets(self):
        sets_struct = {
            self.service_sets[0]: sorted(self.service_types_names),
            self.service_sets[1]: [],
            self.service_sets[2]: sorted(self.service_types_names[2:]),
        }
        for s, t in sets_struct.items():
            self.add_to_service_set(s, t)

        result = handle_action('view_service_sets', {'login': self.test_client_login,
            'password': self.test_client_password,})
        self.assertEqual('ok', result['status'])
        service_sets_info = result['service_sets']
        self.assertEqual(len(self.service_sets), len(service_sets_info))
        for i in service_sets_info:
            if i['name'] in sets_struct:
                self.assertEqual(sets_struct[i['name']], i['types'])
            else:
                self.assertEqual([], i['types'])


if __name__ == '__main__':
    unittest.main()