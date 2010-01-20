import unittest

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action
from helixtariff.error import ServiceSetNotEmpty, ServiceTypeUsed,\
    ServiceSetNotFound


class ServiceSetTestCase(ServiceTestCase):
    service_sets = ['automatic', 'exotic', 'full pack', 'manual']
    service_types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn', 'register dj', 'prolong dj']

    def setUp(self):
        super(ServiceSetTestCase, self).setUp()
        self.add_service_types(self.service_types_names)
        self.add_service_sets(self.service_sets, self.service_types_names)

    def test_add_service_sets(self):
        pass

    def test_modify_service_set(self):
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
        handle_action('modify_service_set', data)

        s_new = self.get_service_set_by_name(client.id, new_name)
        self.assertEqual(s_old.id, s_new.id)
        self.assertEquals(s_new.name, new_name)

        new_service_types_names = self.service_types_names[len(self.service_types_names)/2:]
        data = {
            'login': client.login,
            'password': self.test_client_password,
            'name': new_name,
            'new_service_types': new_service_types_names
        }
        handle_action('modify_service_set', data)

        s_new = self.get_service_set_by_name(client.id, new_name)
        self.assertEqual(s_old.id, s_new.id)
        self.assertEquals(s_new.name, new_name)
        actual_service_types_names = [t.name for t in self.get_service_types_by_service_set_name(client.id, new_name)]
        self.assertEquals(sorted(new_service_types_names), sorted(actual_service_types_names))
        service_set = self.get_service_set_by_name(client.id, new_name)
        self.assertEqual(len(actual_service_types_names), len(self.get_service_set_rows(service_set)))

    def test_modify_service_set_with_binded_rules(self):
        service_set_name = self.service_sets[0]
        service_type_name = self.service_types_names[0]
        tariff_name = 't0'
        self.add_tariff(service_set_name, tariff_name, False, None)
        self.add_rule(tariff_name, service_type_name, 'price = 2.01')
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': service_set_name,
            'new_service_types': self.service_types_names[1:]
        }
        self.assertRaises(ServiceTypeUsed, handle_action, 'modify_service_set', data)

        another_service_set_name = 'another %s' % service_set_name
        self.add_service_sets([another_service_set_name], self.service_types_names)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': another_service_set_name,
            'new_service_types': self.service_types_names[1:]
        }
        response = handle_action('modify_service_set', data)
        self.assertEqual('ok', response['status'])

    def test_delete_service_set(self):
        name = self.service_sets[0]
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': name
        }
        self.assertRaises(ServiceSetNotEmpty, handle_action, 'delete_service_set', data)

        client_id = self.get_client_by_login(self.test_client_login).id
        service_type = self.get_service_set_by_name(client_id, name)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': name,
            'new_service_types': []
        }
        handle_action('modify_service_set', data)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': name
        }
        handle_action('delete_service_set', data)
        self.assertRaises(ServiceSetNotFound, self.get_service_set_by_name, client_id, name)
        self.assertEqual([], self.get_service_set_rows(service_type))

    def test_delete_nonempty_service_set_failure(self):
        name = self.service_sets[0]
        types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
        self.modify_service_set(name, new_service_types=types_names)
        self.assertRaises(ServiceSetNotEmpty, handle_action,
            'delete_service_set',
            {
                'login': self.test_client_login,
                'password': self.test_client_password,
                'name': name
            }
        )

    def test_get_service_set(self):
        service_set_name = self.service_sets[0]
        self.modify_service_set(service_set_name, new_service_types=self.service_types_names)
        response = handle_action('get_service_set', {'login': self.test_client_login,
            'password': self.test_client_password, 'name': service_set_name,})
        self.assertEqual('ok', response['status'])
        self.assertEqual(service_set_name, response['name'])
        self.assertEquals(sorted(self.service_types_names), sorted(response['service_types']))

    def test_view_service_sets(self):
        sets_struct = {
            self.service_sets[0]: sorted(self.service_types_names),
            self.service_sets[1]: [],
            self.service_sets[2]: sorted(self.service_types_names[2:]),
        }
        for s, t in sets_struct.items():
            self.modify_service_set(s, new_service_types=t)

        response = handle_action('view_service_sets', {'login': self.test_client_login,
            'password': self.test_client_password,})
        self.assertEqual('ok', response['status'])
        service_sets_info = response['service_sets']
        self.assertEqual(len(self.service_sets), len(service_sets_info))
        for i in service_sets_info:
            n = i['name']
            if n in sets_struct:
                self.assertEqual(sets_struct[n], i['service_types'])

    def test_view_empty_service_sets(self):
        login = 'test'
        password = 'qazwsx'
        self.add_client(login, password)
        response = handle_action('view_service_sets', {'login': login, 'password': password})
        self.assertEqual('ok', response['status'])
        self.assertEqual([], response['service_sets'])


if __name__ == '__main__':
    unittest.main()