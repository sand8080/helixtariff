import unittest

from helixcore.server.exceptions import DataIntegrityError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class ServiceSetDescrTestCase(ServiceTestCase):
    name = 'automatic operations'

    def test_add_service_set_descr(self):
        self.add_descrs([self.name])

    def test_modify_service_set_descr(self):
        self.test_add_service_set_descr()
        t_old = self.get_service_set_descr_by_name(self.name)

        new_name = 'new' + self.name
        data = {'name': self.name, 'new_name': new_name}
        handle_action('modify_service_set_descr', data)

        t_new = self.get_service_set_descr_by_name(new_name)
        self.assertEqual(t_old.id, t_new.id)
        self.assertEquals(t_new.name, new_name)

    def test_delete_service_set_descr(self):
        self.test_add_service_set_descr()
        handle_action('delete_service_set_descr', {'name': self.name})
        self.assertRaises(DataIntegrityError, self.get_service_set_descr_by_name, self.name)


if __name__ == '__main__':
    unittest.main()