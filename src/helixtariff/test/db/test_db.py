import unittest

from helixtariff.test.db_based_test import ServiceTestCase

import  helixcore.mapping.actions as mapping

from helixtariff.conf.db import transaction


class TestDbTestCase(ServiceTestCase):
    def setUp(self):
        super(TestDbTestCase, self).setUp()

#    @transaction()
    def test_lock_order(self):
        client = self.get_root_client()
        service_types_names = ['a', 'b', 'c']
        self.add_service_types(service_types_names)
        service_sets = ['one']
        self.add_service_sets(service_sets, service_types_names)
#        self.add_service_sets(service_sets, service_types_names)


if __name__ == '__main__':
    unittest.main()