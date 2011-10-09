import unittest

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase


class TarificationObjectTestCase(ActorLogicTestCase):
    def test_add_tarification_object(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'name': 'Product one'}
        resp = self.add_tarification_object(**req)
        self.check_response_ok(resp)

#    def test_modify_service_type(self):
#        self.add_service_types([self.st_name])
#        old_name = self.st_name
#        t_old = self.get_service_type(self.operator, old_name)
#
#        new_name = 'new' + old_name
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'name': old_name,
#            'new_name': new_name
#        }
#        self.handle_action('modify_service_type', data)
#
#        t_new = self.get_service_type(self.operator, new_name)
#        self.assertEqual(t_old.id, t_new.id)
#        self.assertEquals(t_new.name, new_name)
#
#    def test_delete_service_type(self):
#        self.add_service_types([self.st_name])
#        self.handle_action(
#            'delete_service_type',
#            {
#                'login': self.test_login,
#                'password': self.test_password,
#                'name': self.st_name,
#            }
#        )
#        self.assertRaises(ServiceTypeNotFound, self.get_service_type,
#            self.operator, self.st_name)
#
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'name': self.st_name,
#        }
#        self.assertRaises(RequestProcessingError, self.handle_action, 'delete_service_type', data)
#
#    def test_delete_used_service_type(self):
#        st_names = [self.st_name]
#        self.add_service_types(st_names)
#        ss_names = ['s0']
#        self.add_service_sets(ss_names, st_names)
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'name': self.st_name,
#        }
#        self.assertRaises(RequestProcessingError, self.handle_action, 'delete_service_type', data)
#
#    def test_view_empty_service_types(self):
#        response = self.handle_action('view_service_types', {'login': self.test_login,
#            'password': self.test_password})
#        self.assertTrue('service_types' in response)
#        self.assertEqual([], response['service_types'])
#
#    def test_view_empty_service_types_detailed(self):
#        response = self.handle_action('view_service_types_detailed', {'login': self.test_login,
#            'password': self.test_password})
#        self.assertTrue('service_types' in response)
#        self.assertEqual([], response['service_types'])
#
#    def test_view_service_types_detailed_without_service_set(self):
#        self.add_service_types([self.st_name])
#        response = self.handle_action('view_service_types_detailed', {'login': self.test_login,
#            'password': self.test_password})
#        expected_st_info = [{'service_sets': [], 'name': self.st_name}]
#        self.assertTrue('service_types' in response)
#        self.assertEqual(expected_st_info, response['service_types'])
#
#    def test_view_service_types(self):
#        types = ['one', 'two', 'three']
#        self.add_service_types(types)
#        response = self.handle_action('view_service_types', {'login': self.test_login,
#            'password': self.test_password})
#        self.assertTrue('service_types' in response)
#        self.assertEqual(types, response['service_types'])
#
#    def test_view_service_types_invalid(self):
#        self.assertRaises(RequestProcessingError, self.handle_action, 'view_service_types', {'login': 'fake',
#            'password': self.test_password})
#
#    def test_view_service_types_detailed(self):
#        types = ['one', 'two', 'three']
#        self.add_service_types(types)
#        ss_struct = {
#            's0': types[1:],
#            's1': [],
#            's2': types,
#        }
#        st_struct = {}
#        for ss_name, st_names in ss_struct.items():
#            for t_name in st_names:
#                if t_name not in st_struct:
#                    st_struct[t_name] = set()
#                st_struct[t_name].add(ss_name)
#
#        for ss_name, st_names in ss_struct.items():
#            self.add_service_sets([ss_name], st_names)
#        response = self.handle_action('view_service_types_detailed', {'login': self.test_login,
#            'password': self.test_password})
#        self.assertEqual('ok', response['status'])
#        service_types_info = response['service_types']
#        for st_info in service_types_info:
#            st_name = st_info['name']
#            self.assertEqual(sorted(list(st_struct[st_name])), st_info['service_sets'])


if __name__ == '__main__':
    unittest.main()