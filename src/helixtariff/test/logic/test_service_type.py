import unittest

from helixcore.server.exceptions import DataIntegrityError

from helixtariff.test.db_based_test import DbBasedTestCase
from helixtariff.conf.db import transaction
from helixtariff.logic.actions import handle_action
from helixtariff.logic.selector import get_service_type_by_name


class ServiceTypeTestCase(DbBasedTestCase):
    add_data = {'name': 'registration ru'}

    @transaction()
    def get_service_type(self, name, curs=None):
        return get_service_type_by_name(curs, name)

    def test_add_serveice_type(self):
        handle_action('add_service_type', self.add_data)
        t = self.get_service_type(self.add_data['name'])
        self.assertTrue(t.id > 0)
        self.assertEquals(t.name, self.add_data['name'])

    def test_modify_serveice_type(self):
        self.test_add_serveice_type()
        old_name = self.add_data['name']
        t_old = self.get_service_type(old_name)

        new_name = 'new' + old_name
        data = {'name': old_name, 'new_name': new_name}
        handle_action('modify_service_type', data)

        t_new = self.get_service_type(new_name)
        self.assertEqual(t_old.id, t_new.id)
        self.assertEquals(t_new.name, new_name)

    def test_delete_serveice_type(self):
        self.test_add_serveice_type()
        handle_action('delete_service_type', self.add_data)
        self.assertRaises(DataIntegrityError, self.get_service_type, self.add_data['name'])


if __name__ == '__main__':
    unittest.main()