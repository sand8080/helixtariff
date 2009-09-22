from helixtariff.domain.objects import ServiceType
from helixcore.server.exceptions import DataIntegrityError
import unittest

from helixtariff.test.db_based_test import DbBasedTestCase
from helixtariff.conf.db import transaction

from helixtariff.logic.actions import handle_action
from helixtariff.logic.selector import get_service_set_descr_by_name, get_service_type_by_name, \
    get_service_types_by_descr_name

#from helixtariff.test.logic.test_service_type import ServiceTypeTestCase
#from helixtariff.test.logic.test_service_set_descr import ServiceSetDescrTestCase as _joker

class ServiceSetTestCase(DbBasedTestCase):
    service_set_desrs = ['automatic', 'exotic', 'full pack', 'manual']
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

    def add_to_service_set(self, name, types):
        data = {'name': name, 'types': types}
        handle_action('add_to_service_set', data)
        types = self.get_service_types_by_descr_name(data['name'])
        expected_types_names = data['types']
        self.assertEqual(len(expected_types_names), len(types))
        for idx, t in enumerate(types):
            self.assertEqual(expected_types_names[idx], t.name)

    def test_add_to_service_set(self):
        self.add_to_service_set('automatic', ['register ru', 'prolong ru', 'register hn', 'prolong hn'])

    def test_delete_from_service_set(self):
        service_set_descr = 'automatic'
        types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
        expected_names = types_names[1:]
        self.add_to_service_set(service_set_descr, types_names)
        handle_action('delete_from_service_set', {'name': service_set_descr, 'types': [types_names[0]]})

        actual_types = self.get_service_types_by_descr_name(service_set_descr)
        self.assertEqual(len(expected_names), len(actual_types))
        for idx, t in enumerate(actual_types):
            self.assertEqual(expected_names[idx], t.name)

    def test_delete_service_set(self):
        service_set_descr = 'automatic'
        types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
        self.add_to_service_set(service_set_descr, types_names)
        handle_action('delete_service_set', {'name': service_set_descr})

        actual_types = self.get_service_types_by_descr_name(service_set_descr)
        self.assertEqual(0, len(actual_types))


if __name__ == '__main__':
    unittest.main()