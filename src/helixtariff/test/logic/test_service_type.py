import unittest

from helixcore.server.exceptions import DataIntegrityError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class ServiceTypeTestCase(ServiceTestCase):
    descr_name = 'registration ru'

    def setUp(self):
        super(ServiceTypeTestCase, self).setUp()
        self.client = self.get_root_client()

    def test_add_service_type(self):
        self.add_types(self.client.id, [self.descr_name])

    def test_modify_service_type(self):
        self.test_add_service_type()
        old_name = self.descr_name
        t_old = self.get_service_type_by_name(self.client.id, old_name)

        new_name = 'new' + old_name
        data = {'name': old_name, 'new_name': new_name}
        handle_action('modify_service_type', data)

        t_new = self.get_service_type_by_name(self.client.id, new_name)
        self.assertEqual(t_old.id, t_new.id)
        self.assertEquals(t_new.name, new_name)

    def test_delete_service_type(self):
        self.test_add_service_type()
        handle_action('delete_service_type', {'name': self.descr_name})
        self.assertRaises(DataIntegrityError, self.get_service_type_by_name, self.client.id, self.descr_name)


if __name__ == '__main__':
    unittest.main()