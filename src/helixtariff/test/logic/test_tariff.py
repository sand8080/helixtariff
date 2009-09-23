import unittest

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.conf.db import transaction

from helixtariff.logic.actions import handle_action
from helixtariff.logic.selector import get_service_types_by_descr_name


class ServiceTariffTestCase(ServiceTestCase):
    service_types = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
    service_set_desr = 'automatic'
    client_id = 'coyote client 34'
    name = 'happy new year'

    def setUp(self):
        super(ServiceTariffTestCase, self).setUp()
        self.add_descrs([self.service_set_desr])
        self.add_types(self.service_types)
        self.add_to_service_set(self.service_set_desr, self.service_types)

    def test_add_tariff(self):
        self.add_tariff(self.service_set_desr, self.client_id, self.name)

    def test_modify_tariff(self):
        pass

#    def test_delete_from_service_set(self):
#        service_set_descr = 'automatic'
#        types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
#        expected_names = types_names[1:]
#        self.add_to_service_set(service_set_descr, types_names)
#        handle_action('delete_from_service_set', {'name': service_set_descr, 'types': [types_names[0]]})
#
#        actual_types = self.get_service_types_by_descr_name(service_set_descr)
#        self.assertEqual(len(expected_names), len(actual_types))
#        for idx, t in enumerate(actual_types):
#            self.assertEqual(expected_names[idx], t.name)
#
#    def test_delete_service_set(self):
#        service_set_descr = 'automatic'
#        types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
#        self.add_to_service_set(service_set_descr, types_names)
#        handle_action('delete_service_set', {'name': service_set_descr})
#
#        actual_types = self.get_service_types_by_descr_name(service_set_descr)
#        self.assertEqual(0, len(actual_types))


if __name__ == '__main__':
    unittest.main()