import unittest

from helixcore.server.errors import RequestProcessingError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.error import (ServiceSetNotEmpty, ServiceTypeUsed,
    ServiceSetNotFound)


class ServiceSetTestCase(ServiceTestCase):
    ss_names = ['automatic', 'exotic', 'full pack', 'manual']
    st_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn', 'register dj', 'prolong dj']

    def setUp(self):
        super(ServiceSetTestCase, self).setUp()
        self.add_service_types(self.st_names)
        self.add_service_sets(self.ss_names, self.st_names)

    def test_add_service_sets(self):
        self.assertRaises(RequestProcessingError, self.add_service_sets, self.ss_names, self.st_names)

    def test_modify_service_set(self):
        name = self.ss_names[0]
        operator = self.get_operator_by_login(self.test_login)
        s_old = self.get_service_set_by_name(operator, name)

        new_name = 'new' + name
        data = {
            'login': operator.login,
            'password': self.test_password,
            'name': name,
            'new_name': new_name
        }
        self.handle_action('modify_service_set', data)

        s_new = self.get_service_set_by_name(operator, new_name)
        self.assertEqual(s_old.id, s_new.id)
        self.assertEquals(s_new.name, new_name)

        new_st_names = self.st_names[len(self.st_names)/2:]
        data = {
            'login': operator.login,
            'password': self.test_password,
            'name': new_name,
            'new_service_types': new_st_names
        }
        self.handle_action('modify_service_set', data)

        s_new = self.get_service_set_by_name(operator, new_name)
        self.assertEqual(s_old.id, s_new.id)
        self.assertEquals(s_new.name, new_name)
        actual_service_types = self.get_service_types_by_service_set_name(operator, new_name)
        actual_service_types_names = [t.name for t in actual_service_types]
        self.assertEquals(sorted(new_st_names), sorted(actual_service_types_names))
        service_set = self.get_service_set_by_name(operator, new_name)
        self.assertEqual(len(actual_service_types_names), len(self.get_service_set_rows(service_set)))

        data = {
            'login': operator.login,
            'password': self.test_password,
            'name': '%s_fake' % new_name,
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'modify_service_set', data)

        data = {
            'login': operator.login,
            'password': self.test_password,
            'name': new_name,
            'new_service_types': new_st_names + ['fake_service_type_name']
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'modify_service_set', data)

    def test_modify_service_set_with_binded_rules(self):
        ss_name = self.ss_names[0]
        st_name = self.st_names[0]
        t_name = 't0'
        self.add_tariff(ss_name, t_name, False, None)
        self.save_draft_rule(t_name, st_name, 'price = 2.01', True)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'name': ss_name,
            'new_service_types': self.st_names[1:]
        }
        self.assertRaises(ServiceTypeUsed, self.handle_action, 'modify_service_set', data)

        another_ss_name = 'another %s' % ss_name
        self.add_service_sets([another_ss_name], self.st_names)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'name': another_ss_name,
            'new_service_types': self.st_names[1:]
        }
        response = self.handle_action('modify_service_set', data)
        self.assertEqual('ok', response['status'])

    def test_delete_service_set(self):
        ss_name = self.ss_names[0]
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'name': ss_name
        }
        self.assertRaises(ServiceSetNotEmpty, self.handle_action, 'delete_service_set', data)

        operator = self.get_operator_by_login(self.test_login)
        service_type = self.get_service_set_by_name(operator, ss_name)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'name': ss_name,
            'new_service_types': []
        }
        self.handle_action('modify_service_set', data)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'name': ss_name
        }
        self.handle_action('delete_service_set', data)
        self.assertRaises(ServiceSetNotFound, self.get_service_set_by_name, operator, ss_name)
        self.assertEqual([], self.get_service_set_rows(service_type))

    def test_delete_nonempty_service_set_failure(self):
        ss_name = self.ss_names[0]
        st_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
        self.modify_service_set(ss_name, new_service_types=st_names)
        self.assertRaises(ServiceSetNotEmpty, self.handle_action,
            'delete_service_set',
            {
                'login': self.test_login,
                'password': self.test_password,
                'name': ss_name
            }
        )

    def test_get_service_set(self):
        ss_name = self.ss_names[0]
        self.modify_service_set(ss_name, new_service_types=self.st_names)
        response = self.handle_action('get_service_set', {'login': self.test_login,
            'password': self.test_password, 'name': ss_name,})
        self.assertEqual('ok', response['status'])
        self.assertEqual(ss_name, response['name'])
        self.assertEquals(sorted(self.st_names), sorted(response['service_types']))

    def test_get_service_set_detailed(self):
        ss_name = self.ss_names[0]
        response = self.handle_action('get_service_set_detailed', {'login': self.test_login,
            'password': self.test_password, 'name': ss_name,})
        self.assertEqual('ok', response['status'])
        self.assertEqual(ss_name, response['name'])
        self.assertEquals(sorted(self.st_names), response['service_types'])
        self.assertEquals([], response['tariffs'])

        t_names = ['t1', 't0', 't3']
        for n in t_names:
            self.add_tariff(ss_name, n, False, None)
        response = self.handle_action('get_service_set_detailed', {'login': self.test_login,
            'password': self.test_password, 'name': ss_name,})
        self.assertEqual('ok', response['status'])
        self.assertEqual(ss_name, response['name'])
        self.assertEquals(sorted(self.st_names), response['service_types'])
        self.assertEquals(sorted(t_names), response['tariffs'])

    def test_view_service_sets(self):
        sets_struct = {
            self.ss_names[0]: sorted(self.st_names),
            self.ss_names[1]: [],
            self.ss_names[2]: sorted(self.st_names[2:]),
        }
        for s, t in sets_struct.items():
            self.modify_service_set(s, new_service_types=t)

        response = self.handle_action('view_service_sets', {'login': self.test_login,
            'password': self.test_password,})
        self.assertEqual('ok', response['status'])
        service_sets_info = response['service_sets']
        self.assertEqual(len(self.ss_names), len(service_sets_info))
        for i in service_sets_info:
            n = i['name']
            if n in sets_struct:
                self.assertEqual(sets_struct[n], i['service_types'])

    def test_view_service_sets_detailed(self):
        sets_struct = {
            self.ss_names[0]: (sorted(self.st_names), 't0'),
            self.ss_names[1]: ([], 't1'),
            self.ss_names[2]: (sorted(self.st_names[2:]), 't2'),
        }
        for ss_name, (st_names, t_name) in sets_struct.items():
            self.modify_service_set(ss_name, new_service_types=st_names)
            self.add_tariff(ss_name, t_name, False, None)

        response = self.handle_action('view_service_sets_detailed', {'login': self.test_login,
            'password': self.test_password})
        self.assertEqual('ok', response['status'])
        service_sets_info = response['service_sets']
        self.assertEqual(len(self.ss_names), len(service_sets_info))
        for i in service_sets_info:
            n = i['name']
            if n in sets_struct:
                st_names, t_name = sets_struct[n]
                self.assertEqual(st_names, i['service_types'])
                self.assertEqual([t_name], i['tariffs'])

    def test_view_empty_service_sets(self):
        login = 'test'
        password = 'qazwsx'
        self.add_operator(login, password)
        response = self.handle_action('view_service_sets', {'login': login, 'password': password})
        self.assertEqual('ok', response['status'])
        self.assertEqual([], response['service_sets'])


if __name__ == '__main__':
    unittest.main()