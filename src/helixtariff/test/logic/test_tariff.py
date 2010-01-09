from helixtariff.error import TariffNotFound
import unittest

from helixcore.server.exceptions import DataIntegrityError
from helixcore.db.wrapper import EmptyResultSetError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


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
        self.add_service_sets([self.service_set_name])
        self.add_types(self.service_types_names)
        self.add_to_service_set(self.service_set_name, self.service_types_names)

    def test_add_tariff(self):
        self.add_tariff(self.service_set_name, self.name, self.in_archive, None)
        t = self.get_tariff(self.root_client_id, self.name)
        self.add_tariff(self.service_set_name, 'child of %s' % self.name, self.in_archive, t.name)

    def test_add_tariff_failure(self):
        self.assertRaises(EmptyResultSetError, self.add_tariff, self.service_set_name + 'fake',
            self.name, self.in_archive, None
        )
        self.add_tariff(self.service_set_name, self.name, self.in_archive, None)
        self.assertRaises(DataIntegrityError, self.add_tariff, self.service_set_name,
            self.name, self.in_archive, None
        )

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
        self.test_add_tariff()
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.name,
        }
        handle_action('modify_tariff', data)
        t = self.get_tariff(self.root_client_id, self.name)
        self.assertEqual(self.name, t.name)
        self.assertEqual(self.root_client_id, t.client_id)

    def test_delete_tariff_failure(self):
        self.test_add_tariff()
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.name,
        }
        self.assertRaises(DataIntegrityError, handle_action, 'delete_tariff', data)

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
        result = handle_action('get_tariff', data)
        self.assertTrue('tariff' in result)
        tariff_data = result['tariff']
        self.assertEqual(parent_name, tariff_data['name'])
        self.assertEqual(self.service_set_name, tariff_data['service_set'])
        self.assertEqual(None, tariff_data['parent_tariff'])
        self.assertEqual(self.in_archive, tariff_data['in_archive'])

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': child_name
        }
        result = handle_action('get_tariff', data)
        self.assertTrue('tariff' in result)
        tariff_data = result['tariff']
        self.assertEqual(child_name, tariff_data['name'])
        self.assertEqual(self.service_set_name, tariff_data['service_set'])
        self.assertEqual(parent_name, tariff_data['parent_tariff'])
        self.assertEqual(self.in_archive, tariff_data['in_archive'])

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
        result = handle_action('get_tariff_detailed', data)
        self.assertTrue('tariff' in result)
        tariff_data = result['tariff']
        self.assertEqual(parent_name, tariff_data['name'])
        self.assertEqual(self.service_set_name, tariff_data['service_set'])
        self.assertEqual(sorted(self.service_types_names), tariff_data['types'])
        self.assertEqual(None, tariff_data['parent_tariff'])
        self.assertEqual(self.in_archive, tariff_data['in_archive'])

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': child_name
        }
        result = handle_action('get_tariff_detailed', data)
        self.assertTrue('tariff' in result)
        tariff_data = result['tariff']
        self.assertEqual(child_name, tariff_data['name'])
        self.assertEqual(self.service_set_name, tariff_data['service_set'])
        self.assertEqual(sorted(self.service_types_names), tariff_data['types'])
        self.assertEqual(parent_name, tariff_data['parent_tariff'])
        self.assertEqual(self.in_archive, tariff_data['in_archive'])

        empty_set_descr_name = 'empty'
        tariff_name = 'no services'
        self.add_service_sets([empty_set_descr_name])
        self.add_tariff(empty_set_descr_name, tariff_name, False, parent_name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': tariff_name
        }
        result = handle_action('get_tariff_detailed', data)
        self.assertTrue('tariff' in result)
        tariff_data = result['tariff']
        self.assertEqual(tariff_name, tariff_data['name'])
        self.assertEqual(empty_set_descr_name, tariff_data['service_set'])
        self.assertEqual([], tariff_data['types'])
        self.assertEqual(False, tariff_data['in_archive'])
        self.assertEqual(parent_name, tariff_data['parent_tariff'])

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
            {'parent_tariff': None, 'name': parent_name,
                'service_set': self.service_set_name, 'in_archive': self.in_archive},
            tariffs[0]
        )
        self.assertEqual(
            {'parent_tariff': parent_name, 'name': child_name,
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
            {'parent_tariff': None, 'name': parent_name, 'service_set': self.service_set_name,
                'in_archive': self.in_archive, 'types': types_names},
            tariffs[0]
        )
        self.assertEqual(
            {'parent_tariff': parent_name, 'name': child_name, 'service_set': self.service_set_name,
                'in_archive': self.in_archive, 'types': types_names},
            tariffs[1]
        )


if __name__ == '__main__':
    unittest.main()