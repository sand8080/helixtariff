import unittest

from helixcore.server.exceptions import DataIntegrityError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action
from helixtariff.error import TariffNotFound, TariffCycleError,\
    ServiceSetNotFound, TariffUsed


class TariffTestCase(ServiceTestCase):
    service_types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
    service_set_name = 'automatic'
    name = 'happy new year'
    in_archive = False

    @property
    def root_client_id(self):
        return self.get_root_client().id

    def setUp(self):
        super(TariffTestCase, self).setUp()
        self.add_service_types(self.service_types_names)
        self.add_service_sets([self.service_set_name], self.service_types_names)

    def test_add_tariff(self):
        self.add_tariff(self.service_set_name, self.name, self.in_archive, None)
        t = self.get_tariff(self.root_client_id, self.name)
        self.add_tariff(self.service_set_name, 'child of %s' % self.name, self.in_archive, t.name)

    def test_add_tariff_failure(self):
        self.assertRaises(ServiceSetNotFound, self.add_tariff, self.service_set_name + 'fake',
            self.name, self.in_archive, None
        )
        self.add_tariff(self.service_set_name, self.name, self.in_archive, None)
        self.assertRaises(DataIntegrityError, self.add_tariff, self.service_set_name,
            self.name, self.in_archive, None
        )

    def test_tariffs_cycle(self):
        tariff_0 = 'tariff 0'
        self.add_tariff(self.service_set_name, tariff_0, False, None)
        tariff_1 = 'tariff 1'
        self.add_tariff(self.service_set_name, tariff_1, False, tariff_0)
        tariff_2 = 'tariff 2'
        self.add_tariff(self.service_set_name, tariff_2, False, tariff_0)
        self.assertRaises(TariffCycleError, self.modify_tariff, tariff_0, tariff_2)

    def test_modify_tariff(self):
        self.test_add_tariff()
        new_name = 'new' + self.name
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.name,
            'new_name': new_name,
            'new_in_archive': not self.in_archive,
        }
        handle_action('modify_tariff', data)
        t = self.get_tariff(self.root_client_id, new_name)
        self.assertEqual(new_name, t.name)
        self.assertEqual(self.root_client_id, t.client_id)
        self.assertEqual(not self.in_archive, t.in_archive)

    def test_modify_tariff_service_set_without_rules(self):
        self.add_tariff(self.service_set_name, self.name, False, None)
        new_service_set_name = 'new_%s' % self.service_set_name
        self.add_service_sets([new_service_set_name], self.service_types_names[2:])
        client_id = self.get_root_client().id
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.name,
            'new_service_set': new_service_set_name,
        }
        handle_action('modify_tariff', data)
        t = self.get_tariff(self.root_client_id, self.name)
        new_service_set = self.get_service_set_by_name(client_id, new_service_set_name)
        self.assertEqual(self.name, t.name)
        self.assertEqual(client_id, t.client_id)
        self.assertEqual(new_service_set.id, t.service_set_id)

    def test_modify_parent_tariff(self):
        parent_name = 'parent'
        self.add_tariff(self.service_set_name, parent_name, self.in_archive, None)
        child_name = 'child'
        self.add_tariff(self.service_set_name, child_name, self.in_archive, parent_name)
        new_child_name = 'new' + child_name
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': child_name,
            'new_name': new_child_name,
            'new_in_archive': not self.in_archive,
            'new_parent_tariff': None,
        }
        handle_action('modify_tariff', data)
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
        handle_action('modify_tariff', data)
        t = self.get_tariff(self.root_client_id, new_child_name)
        self.assertEqual(new_child_name, t.name)
        self.assertEqual(self.root_client_id, t.client_id)
        self.assertEqual(self.get_tariff(self.root_client_id, parent_name).id, t.parent_id)

    def test_modify_tariff_do_nothing(self):
        self.add_tariff(self.service_set_name, self.name, self.in_archive, None)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.name,
        }
        handle_action('modify_tariff', data)
        t = self.get_tariff(self.root_client_id, self.name)
        self.assertEqual(self.name, t.name)
        self.assertEqual(self.root_client_id, t.client_id)

    def test_delete_parent_tariff(self):
        self.add_tariff(self.service_set_name, self.name, self.in_archive, None)
        self.add_tariff(self.service_set_name, 'child of %s' % self.name, self.in_archive, self.name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.name,
        }
        self.assertRaises(TariffUsed, handle_action, 'delete_tariff', data)

    def test_delete_tariff(self):
        parent_name = 'parent'
        self.add_tariff(self.service_set_name, parent_name, self.in_archive, None)
        child_name = 'child'
        self.add_tariff(self.service_set_name, child_name, self.in_archive, parent_name)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': child_name,
        }
        handle_action('delete_tariff', data)
        self.assertRaises(TariffNotFound, self.get_tariff, self.root_client_id, child_name)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': parent_name,
        }
        handle_action('delete_tariff', data)
        self.assertRaises(TariffNotFound, self.get_tariff, self.root_client_id, parent_name)

    def test_delete_tariff_with_rules(self):
        self.add_tariff(self.service_set_name, self.name, self.in_archive, None)
        self.add_rule(self.name, self.service_types_names[0], 'price = 1.0')
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.name,
        }
        self.assertRaises(TariffUsed, handle_action, 'delete_tariff', data)

    def test_get_tariff(self):
        parent_name = 'parent'
        self.add_tariff(self.service_set_name, parent_name, self.in_archive, None)
        child_name = 'child'
        self.add_tariff(self.service_set_name, child_name, self.in_archive, parent_name)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': parent_name
        }
        response = handle_action('get_tariff', data)
        self.assertEqual(parent_name, response['name'])
        self.assertEqual(self.service_set_name, response['service_set'])
        self.assertEqual([parent_name], response['tariffs_chain'])
        self.assertEqual(self.in_archive, response['in_archive'])

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': child_name
        }
        response = handle_action('get_tariff', data)
        self.assertEqual(child_name, response['name'])
        self.assertEqual(self.service_set_name, response['service_set'])
        self.assertEqual([child_name, parent_name], response['tariffs_chain'])
        self.assertEqual(self.in_archive, response['in_archive'])

    def test_get_tariff_detailed(self):
        parent_name = 'parent'
        self.add_tariff(self.service_set_name, parent_name, self.in_archive, None)
        child_name = 'child'
        self.add_tariff(self.service_set_name, child_name, self.in_archive, parent_name)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': parent_name
        }
        response = handle_action('get_tariff_detailed', data)
        self.assertEqual(parent_name, response['name'])
        self.assertEqual(self.service_set_name, response['service_set'])
        self.assertEqual(sorted(self.service_types_names), response['service_types'])
        self.assertEqual([parent_name], response['tariffs_chain'])
        self.assertEqual(self.in_archive, response['in_archive'])

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': child_name
        }
        response = handle_action('get_tariff_detailed', data)
        self.assertEqual(child_name, response['name'])
        self.assertEqual(self.service_set_name, response['service_set'])
        self.assertEqual(sorted(self.service_types_names), response['service_types'])
        self.assertEqual([child_name, parent_name], response['tariffs_chain'])
        self.assertEqual(self.in_archive, response['in_archive'])

        empty_set_name = 'empty'
        tariff_name = 'no services'
        self.add_service_sets([empty_set_name], [])
        self.add_tariff(empty_set_name, tariff_name, False, parent_name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': tariff_name
        }
        response = handle_action('get_tariff_detailed', data)
        self.assertEqual(tariff_name, response['name'])
        self.assertEqual(empty_set_name, response['service_set'])
        self.assertEqual([], response['service_types'])
        self.assertEqual(False, response['in_archive'])
        self.assertEqual([tariff_name, parent_name], response['tariffs_chain'])

    def test_view_tariffs(self):
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
        }
        result = handle_action('view_tariffs', data)
        self.assertTrue('tariffs' in result)
        self.assertEqual([], result['tariffs'])

        parent_name = 'parent'
        self.add_tariff(self.service_set_name, parent_name, self.in_archive, None)
        child_name = 'child'
        self.add_tariff(self.service_set_name, child_name, self.in_archive, parent_name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
        }
        result = handle_action('view_tariffs', data)
        self.assertTrue('tariffs' in result)
        tariffs = result['tariffs']
        self.assertEqual(2, len(tariffs))
        self.assertEqual(
            {'tariffs_chain': [parent_name], 'name': parent_name,
                'service_set': self.service_set_name, 'in_archive': self.in_archive},
            tariffs[0]
        )
        self.assertEqual(
            {'tariffs_chain': [child_name, parent_name], 'name': child_name,
                'service_set': self.service_set_name, 'in_archive': self.in_archive},
            tariffs[1]
        )

    def test_view_detailed_tariffs(self):
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
        }
        result = handle_action('view_detailed_tariffs', data)
        self.assertTrue('tariffs' in result)
        self.assertEqual([], result['tariffs'])

        parent_name = 'parent'
        self.add_tariff(self.service_set_name, parent_name, self.in_archive, None)
        child_name = 'child'
        self.add_tariff(self.service_set_name, child_name, self.in_archive, parent_name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
        }
        result = handle_action('view_detailed_tariffs', data)

        types = self.get_service_types_by_service_set_name(self.root_client_id, self.service_set_name)
        types_names = sorted([t.name for t in types])
        self.assertTrue('tariffs' in result)
        tariffs = result['tariffs']
        self.assertEqual(2, len(tariffs))
        self.assertEqual(
            {'tariffs_chain': [parent_name], 'name': parent_name, 'service_set': self.service_set_name,
                'in_archive': self.in_archive, 'service_types': types_names},
            tariffs[0]
        )
        self.assertEqual(
            {'tariffs_chain': [child_name, parent_name], 'name': child_name, 'service_set': self.service_set_name,
                'in_archive': self.in_archive, 'service_types': types_names},
            tariffs[1]
        )


if __name__ == '__main__':
    unittest.main()