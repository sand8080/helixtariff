from helixtariff.domain.objects import ServiceType
import unittest

from helixtariff.test.db_based_test import DbBasedTestCase
from helixtariff.conf.db import transaction

from helixtariff.logic.actions import handle_action
from helixtariff.logic.selector import get_service_set_descr_by_name, get_service_type_by_name,\
    get_service_types_by_descr_name

#from helixtariff.test.logic.test_service_type import ServiceTypeTestCase
#from helixtariff.test.logic.test_service_set_descr import ServiceSetDescrTestCase as _joker

class ServiceSetTestCase(DbBasedTestCase):
#    add_data = {'name': 'automatic operations'}

    service_set_desrs = ['automatic', 'exotic', 'full pack']
    service_types = ['register ru', 'prolong ru', 'register hn', 'prolong hn', 'register dj', 'prolong dj']

    def setUp(self):
        super(ServiceSetTestCase, self).setUp()
        for d in self.service_set_desrs:
            handle_action('add_service_set_descr', {'name': d})
        for t in self.service_types:
            handle_action('add_service_type', {'name': t})

    @transaction()
    def get_service_types_by_descr_name(self, name, curs=None):
        return get_service_types_by_descr_name(curs, name)

#    @transaction()
#    def get_service_type(self, name, curs=None):
#        return get_service_type_by_name(curs, name)

    def test_add_to_service_set(self):
        data = {
            'name': 'automatic',
            'types': ['register ru', 'prolong ru', 'register hn', 'prolong hn']
        }
        handle_action('add_to_service_set', data)
#        types = self.get_service_types_by_descr_name(data['name'])
#        self.assertTrue(t.id > 0)
#        self.assertEquals(t.name, self.add_data['name'])

#    def test_modify_serveice_set_descr(self):
#        self.test_add_serveice_set_descr()
#        old_name = self.add_data['name']
#        t_old = self.get_service_set_descr(old_name)
#
#        new_name = 'new' + old_name
#        data = {'name': old_name, 'new_name': new_name}
#        handle_action('modify_service_set_descr', data)
#
#        t_new = self.get_service_set_descr(new_name)
#        self.assertEqual(t_old.id, t_new.id)
#        self.assertEquals(t_new.name, new_name)
#
#    def test_delete_serveice_set_descr(self):
#        self.test_add_serveice_set_descr()
#        handle_action('delete_service_set_descr', self.add_data)
#        self.assertRaises(DataIntegrityError, self.get_service_set_descr, self.add_data['name'])


if __name__ == '__main__':
    unittest.main()