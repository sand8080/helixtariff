import unittest

from helixcore.server.exceptions import DataIntegrityError
from helixcore.db.wrapper import EmptyResultSetError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class TariffTestCase(ServiceTestCase):
    service_types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
    service_set_descr_name = 'automatic'
    name = 'happy new year'
    in_archive = False

    @property
    def root_client_id(self):
        return self.get_root_client().id

    def setUp(self):
        super(TariffTestCase, self).setUp()
        self.add_descrs([self.service_set_descr_name])
        self.add_types(self.service_types_names)
        self.add_to_service_set(self.service_set_descr_name, self.service_types_names)

    def test_add_tariff(self):
        self.add_tariff(self.service_set_descr_name, self.name, self.in_archive)

    def test_add_tariff_failure(self):
        self.assertRaises(DataIntegrityError, self.add_tariff, self.service_set_descr_name + 'fake',
            self.name, self.in_archive
        )
        self.add_tariff(self.service_set_descr_name, self.name, self.in_archive)
        self.assertRaises(DataIntegrityError, self.add_tariff, self.service_set_descr_name,
            self.name, self.in_archive
        )

    def test_modify_tariff(self):
        self.test_add_tariff()
        new_name = 'new' + self.name
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.name,
            'new_name': new_name,
            'new_in_archive': not self.in_archive
        }
        handle_action('modify_tariff', data)
        t = self.get_tariff(self.root_client_id, new_name)
        self.assertEqual(new_name, t.name)
        self.assertEqual(self.root_client_id, t.client_id)

    def test_modify_tariff_do_nothing(self):
        self.test_add_tariff()
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.name
        }
        handle_action('modify_tariff', data)
        t = self.get_tariff(self.root_client_id, self.name)
        self.assertEqual(self.name, t.name)
        self.assertEqual(self.root_client_id, t.client_id)

    def test_delete_tariff(self):
        self.test_add_tariff()
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': self.name
        }
        handle_action('delete_tariff', data)
        self.assertRaises(EmptyResultSetError, self.get_tariff, self.root_client_id, self.name)


if __name__ == '__main__':
    unittest.main()