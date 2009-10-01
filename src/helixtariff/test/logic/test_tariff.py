import unittest

from helixcore.server.exceptions import DataIntegrityError
from helixcore.db.wrapper import EmptyResultSetError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class TariffTestCase(ServiceTestCase):
    service_types = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
    service_set_descr = 'automatic'
    client_id = 'coyote client 34'
    name = 'happy new year'
    in_archive = False

    def setUp(self):
        super(TariffTestCase, self).setUp()
        self.add_descrs([self.service_set_descr])
        self.add_types(self.service_types)
        self.add_to_service_set(self.service_set_descr, self.service_types)

    def test_add_tariff(self):
        self.add_tariff(self.service_set_descr, self.client_id, self.name, self.in_archive)

    def test_add_tariff_failure(self):
        self.assertRaises(DataIntegrityError, self.add_tariff, self.service_set_descr + 'fake',
            self.client_id, self.name, self.in_archive
        )
        self.add_tariff(self.service_set_descr, self.client_id, self.name, self.in_archive)
        self.assertRaises(DataIntegrityError, self.add_tariff, self.service_set_descr,
            self.client_id, self.name, self.in_archive
        )

    def test_modify_tariff(self):
        self.test_add_tariff()
        new_name = 'new' + self.name
        data = {'client_id': self.client_id, 'name': self.name, 'new_name': new_name, 'new_in_archive': not self.in_archive}
        handle_action('modify_tariff', data)
        t = self.get_tariff(self.client_id, new_name)
        self.assertEqual(new_name, t.name)
        self.assertEqual(self.client_id, t.client_id)

    def test_modify_tariff_do_nothing(self):
        self.test_add_tariff()
        data = {'client_id': self.client_id, 'name': self.name}
        handle_action('modify_tariff', data)
        t = self.get_tariff(self.client_id, self.name)
        self.assertEqual(self.name, t.name)
        self.assertEqual(self.client_id, t.client_id)

    def test_delete_tariff(self):
        self.test_add_tariff()
        data = {'client_id': self.client_id, 'name': self.name}
        handle_action('delete_tariff', data)
        self.assertRaises(EmptyResultSetError, self.get_tariff, self.client_id, self.name)


if __name__ == '__main__':
    unittest.main()