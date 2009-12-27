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
        s_old = self.get_service_set_by_name(name)

        new_name = 'new' + name
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': name,
            'new_name': new_name
        }
        handle_action('rename_service_set', data)

        s_new = self.get_service_set_by_name(new_name)
        self.assertEqual(s_old.id, s_new.id)
        self.assertEquals(s_new.name, new_name)

    def test_delete_service_set(self):
        name = self.service_sets[0]
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': name
        }
        handle_action('delete_service_set', data)
        self.assertRaises(EmptyResultSetError, self.get_service_set_by_name, name)

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
        self.add_to_service_set('automatic', ['register ru', 'prolong ru', 'register hn', 'prolong hn'])

    def test_delete_from_service_set(self):
        service_set_descr = 'automatic'
        types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
        expected_names = types_names[1:]
        self.add_to_service_set(service_set_descr, types_names)
        handle_action(
            'delete_from_service_set',
            {
                'login': self.test_client_login,
                'password': self.test_client_password,
                'name': service_set_descr,
                'types': [types_names[0]]
            }
        )

        actual_types = self.get_service_types_by_descr_name(service_set_descr)
        self.assertEqual(len(expected_names), len(actual_types))
        for idx, t in enumerate(actual_types):
            self.assertEqual(expected_names[idx], t.name)


if __name__ == '__main__':
    unittest.main()