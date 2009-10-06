import unittest

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class ServiceSetTestCase(ServiceTestCase):
    service_set_desrs = ['automatic', 'exotic', 'full pack', 'manual']
    service_types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn', 'register dj', 'prolong dj']

    def setUp(self):
        super(ServiceSetTestCase, self).setUp()
        self.add_descrs(self.service_set_desrs)
        self.add_types(self.service_types_names)

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

    def test_delete_service_set(self):
        service_set_descr = 'automatic'
        types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
        self.add_to_service_set(service_set_descr, types_names)
        handle_action(
            'delete_service_set',
            {
                'login': self.test_client_login,
                'password': self.test_client_password,
                'name': service_set_descr
            }
        )

        actual_types = self.get_service_types_by_descr_name(service_set_descr)
        self.assertEqual(0, len(actual_types))


if __name__ == '__main__':
    unittest.main()