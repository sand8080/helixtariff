from helixcore.server.errors import RequestProcessingError
from helixtariff.domain.objects import Rule
import unittest

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.error import TariffNotFound, RuleNotFound


class TariffTestCase(ServiceTestCase):
    st_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
    ss_name = 'automatic'
    t_name = 'happy new year'
    in_archive = False

    @property
    def root_client_id(self):
        return self.get_root_client().id

    def setUp(self):
        super(TariffTestCase, self).setUp()
        self.add_service_types(self.st_names)
        self.add_service_sets([self.ss_name], self.st_names)

    def test_add_tariff(self):
        self.add_tariff(self.ss_name, self.t_name, self.in_archive, None)
        t = self.get_tariff(self.root_client_id, self.t_name)
        self.add_tariff(self.ss_name, 'child of %s' % self.t_name, self.in_archive, t.name)

        self.assertRaises(RequestProcessingError, self.add_tariff, self.ss_name + 'fake',
            self.t_name, self.in_archive, None)
        self.assertRaises(RequestProcessingError, self.add_tariff, self.ss_name,
            self.t_name, self.in_archive, None)
        self.assertRaises(RequestProcessingError, self.add_tariff, self.ss_name,
            self.t_name, self.in_archive, self.t_name)
        self.assertRaises(RequestProcessingError, self.add_tariff, self.ss_name,
            'tt', self.in_archive, 'tt')

    def test_tariffs_cycle(self):
        tariff_0 = 'tariff 0'
        self.add_tariff(self.ss_name, tariff_0, False, None)
        tariff_1 = 'tariff 1'
        self.add_tariff(self.ss_name, tariff_1, False, tariff_0)
        tariff_2 = 'tariff 2'
        self.add_tariff(self.ss_name, tariff_2, False, tariff_0)
        self.assertRaises(RequestProcessingError, self.modify_tariff, tariff_0, tariff_2)

    def test_modify_tariff(self):
        self.add_tariff(self.ss_name, self.t_name, self.in_archive, None)
        new_name = 'new' + self.t_name
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.t_name,
            'new_name': new_name,
            'new_in_archive': not self.in_archive,
        }
        self.handle_action('modify_tariff', data)
        t = self.get_tariff(self.root_client_id, new_name)
        self.assertEqual(new_name, t.name)
        self.assertEqual(self.root_client_id, t.client_id)
        self.assertEqual(not self.in_archive, t.in_archive)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': 'fake_%s' % self.t_name,
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'modify_tariff', data)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': new_name,
            'new_service_set': 'fake',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'modify_tariff', data)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': new_name,
            'new_parent_tariff': 'fake',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'modify_tariff', data)

    def test_modify_tariff_service_set_without_rules(self):
        self.add_tariff(self.ss_name, self.t_name, False, None)
        new_ss_name = 'new_%s' % self.ss_name
        self.add_service_sets([new_ss_name], self.st_names[2:])
        c_id = self.get_root_client().id
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.t_name,
            'new_service_set': new_ss_name,
        }
        self.handle_action('modify_tariff', data)
        t = self.get_tariff(self.root_client_id, self.t_name)
        new_service_set = self.get_service_set_by_name(c_id, new_ss_name)
        self.assertEqual(self.t_name, t.name)
        self.assertEqual(c_id, t.client_id)
        self.assertEqual(new_service_set.id, t.service_set_id)

    def test_modify_parent_tariff(self):
        parent_name = 'parent'
        self.add_tariff(self.ss_name, parent_name, self.in_archive, None)
        child_name = 'child'
        self.add_tariff(self.ss_name, child_name, self.in_archive, parent_name)
        new_child_name = 'new' + child_name
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': child_name,
            'new_name': new_child_name,
            'new_in_archive': not self.in_archive,
            'new_parent_tariff': None,
        }
        self.handle_action('modify_tariff', data)
        t = self.get_tariff(self.root_client_id, new_child_name)
        self.assertEqual(new_child_name, t.name)
        self.assertEqual(self.root_client_id, t.client_id)
        self.assertEqual(not self.in_archive, t.in_archive)
        self.assertEqual(None, t.parent_id)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': new_child_name,
            'new_parent_tariff': parent_name,
        }
        self.handle_action('modify_tariff', data)
        t = self.get_tariff(self.root_client_id, new_child_name)
        self.assertEqual(new_child_name, t.name)
        self.assertEqual(self.root_client_id, t.client_id)
        self.assertEqual(self.get_tariff(self.root_client_id, parent_name).id, t.parent_id)

    def test_modify_tariff_do_nothing(self):
        self.add_tariff(self.ss_name, self.t_name, self.in_archive, None)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.t_name,
        }
        self.handle_action('modify_tariff', data)
        t = self.get_tariff(self.root_client_id, self.t_name)
        self.assertEqual(self.t_name, t.name)
        self.assertEqual(self.root_client_id, t.client_id)

    def test_delete_parent_tariff(self):
        self.add_tariff(self.ss_name, self.t_name, self.in_archive, None)
        self.add_tariff(self.ss_name, 'child of %s' % self.t_name, self.in_archive, self.t_name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.t_name,
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'delete_tariff', data)

    def test_delete_tariff(self):
        p_name = 'parent'
        self.add_tariff(self.ss_name, p_name, self.in_archive, None)
        ch_name = 'child'
        self.add_tariff(self.ss_name, ch_name, self.in_archive, p_name)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': ch_name,
        }
        self.handle_action('delete_tariff', data)

        c_id = self.get_client_by_login(self.test_client_login).id
        self.assertRaises(TariffNotFound, self.get_tariff, c_id, ch_name)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': p_name,
        }
        self.handle_action('delete_tariff', data)
        self.assertRaises(TariffNotFound, self.get_tariff, c_id, p_name)

    def test_delete_tariff_with_disabled_rules(self):
        self.add_tariff(self.ss_name, self.t_name, self.in_archive, None)
        st_name = self.st_names[0]
        self.save_draft_rule(self.t_name, st_name, 'price = 1.0', True)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.t_name,
        }
        self.make_draft_rules_actual(self.t_name)
        self.assertRaises(RequestProcessingError, self.handle_action, 'delete_tariff', data)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.t_name,
            'service_type': st_name,
            'new_enabled': False,
        }
        self.handle_action('modify_actual_rule', data)

        c_id = self.get_client_by_login(self.test_client_login).id
        tariff = self.get_tariff(c_id, self.t_name)
        service_type = self.get_service_type(c_id, st_name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.t_name,
        }
        self.handle_action('delete_tariff', data)
        self.assertRaises(RuleNotFound, self.get_rule, tariff, service_type, Rule.TYPE_ACTUAL)
        self.assertRaises(TariffNotFound, self.get_tariff, c_id, self.t_name)

    def test_delete_tariff_with_draft_rules(self):
        self.add_tariff(self.ss_name, self.t_name, self.in_archive, None)
        st_name = self.st_names[0]
        self.save_draft_rule(self.t_name, st_name, 'price = 1.0', True)

        c_id = self.get_client_by_login(self.test_client_login).id
        tariff = self.get_tariff(c_id, self.t_name)
        service_type = self.get_service_type(c_id, st_name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.t_name,
        }
        self.handle_action('delete_tariff', data)
        self.assertRaises(RuleNotFound, self.get_rule, tariff, service_type, Rule.TYPE_ACTUAL)
        self.assertRaises(TariffNotFound, self.get_tariff, c_id, self.t_name)

    def test_get_tariff(self):
        pt_name = 'parent'
        self.add_tariff(self.ss_name, pt_name, self.in_archive, None)
        ch_name = 'child'
        self.add_tariff(self.ss_name, ch_name, self.in_archive, pt_name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': pt_name,
        }
        response = self.handle_action('get_tariff', data)
        self.assertEqual(pt_name, response['name'])
        self.assertEqual(self.ss_name, response['service_set'])
        self.assertEqual([pt_name], response['tariffs_chain'])
        self.assertEqual(self.in_archive, response['in_archive'])
        self.assertEqual(None, response['parent_tariff'])

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': ch_name,
        }
        response = self.handle_action('get_tariff', data)
        self.assertEqual(ch_name, response['name'])
        self.assertEqual(self.ss_name, response['service_set'])
        self.assertEqual([ch_name, pt_name], response['tariffs_chain'])
        self.assertEqual(self.in_archive, response['in_archive'])
        self.assertEqual(pt_name, response['parent_tariff'])

    def test_get_tariff_detailed(self):
        p_name = 'parent'
        self.add_tariff(self.ss_name, p_name, self.in_archive, None)
        ch_name = 'child'
        self.add_tariff(self.ss_name, ch_name, self.in_archive, p_name)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': p_name
        }
        response = self.handle_action('get_tariff_detailed', data)
        self.assertEqual(p_name, response['name'])
        self.assertEqual(self.ss_name, response['service_set'])
        self.assertEqual(sorted(self.st_names), response['service_types'])
        self.assertEqual([p_name], response['tariffs_chain'])
        self.assertEqual(self.in_archive, response['in_archive'])
        self.assertEqual(None, response['parent_tariff'])

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': ch_name
        }
        response = self.handle_action('get_tariff_detailed', data)
        self.assertEqual(ch_name, response['name'])
        self.assertEqual(self.ss_name, response['service_set'])
        self.assertEqual(sorted(self.st_names), response['service_types'])
        self.assertEqual([ch_name, p_name], response['tariffs_chain'])
        self.assertEqual(self.in_archive, response['in_archive'])
        self.assertEqual(p_name, response['parent_tariff'])

        empty_s_name = 'empty'
        t_name = 'no services'
        self.add_service_sets([empty_s_name], [])
        self.add_tariff(empty_s_name, t_name, False, p_name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': t_name
        }
        response = self.handle_action('get_tariff_detailed', data)
        self.assertEqual(t_name, response['name'])
        self.assertEqual(empty_s_name, response['service_set'])
        self.assertEqual([], response['service_types'])
        self.assertEqual(False, response['in_archive'])
        self.assertEqual([t_name, p_name], response['tariffs_chain'])
        self.assertEqual(p_name, response['parent_tariff'])

    def test_view_tariffs(self):
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
        }
        result = self.handle_action('view_tariffs', data)
        self.assertTrue('tariffs' in result)
        self.assertEqual([], result['tariffs'])

        pt_name = 'parent'
        self.add_tariff(self.ss_name, pt_name, self.in_archive, None)
        ch_name = 'child'
        self.add_tariff(self.ss_name, ch_name, self.in_archive, pt_name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
        }
        result = self.handle_action('view_tariffs', data)
        self.assertTrue('tariffs' in result)
        actual_t_info = result['tariffs']
        self.assertEqual(2, len(actual_t_info))
        self.assertEqual(
            {'tariffs_chain': [pt_name], 'name': pt_name, 'service_set': self.ss_name,
                'in_archive': self.in_archive, 'parent_tariff': None},
            actual_t_info[0]
        )
        self.assertEqual(
            {'tariffs_chain': [ch_name, pt_name], 'name': ch_name, 'service_set': self.ss_name,
                'in_archive': self.in_archive, 'parent_tariff': pt_name},
            actual_t_info[1]
        )

    def test_view_tariffs_detailed(self):
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
        }
        result = self.handle_action('view_tariffs_detailed', data)
        self.assertTrue('tariffs' in result)
        self.assertEqual([], result['tariffs'])

        p_name = 'parent'
        self.add_tariff(self.ss_name, p_name, self.in_archive, None)
        ch_name = 'child'
        self.add_tariff(self.ss_name, ch_name, self.in_archive, p_name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
        }
        result = self.handle_action('view_tariffs_detailed', data)

        c_id = self.get_client_by_login(self.test_client_login).id
        service_types = self.get_service_types_by_service_set_name(c_id, self.ss_name)
        st_names = sorted([service_type.name for service_type in service_types])
        self.assertTrue('tariffs' in result)
        tariffs = result['tariffs']
        self.assertEqual(2, len(tariffs))
        self.assertEqual(
            {'tariffs_chain': [p_name], 'name': p_name, 'service_set': self.ss_name,
                'in_archive': self.in_archive, 'service_types': st_names, 'parent_tariff': None},
            tariffs[0]
        )
        self.assertEqual(
            {'tariffs_chain': [ch_name, p_name], 'name': ch_name, 'service_set': self.ss_name,
                'in_archive': self.in_archive, 'service_types': st_names, 'parent_tariff': p_name},
            tariffs[1]
        )


if __name__ == '__main__':
    unittest.main()