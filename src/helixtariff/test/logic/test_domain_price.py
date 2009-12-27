import unittest

from helixcore.db.wrapper import EmptyResultSetError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class DomainPriceTestCase(ServiceTestCase):
    service_type_name = 'register ru'
    service_set_name = 'automatic'
    tariff_name = 'moon light'

    def setUp(self):
        super(DomainPriceTestCase, self).setUp()
        self.add_service_sets([self.service_set_name])
        self.add_types([self.service_type_name])
        self.add_to_service_set(self.service_set_name, [self.service_type_name])
        self.add_tariff(self.service_set_name, self.tariff_name, False)
        self.add_rule(self.tariff_name, self.service_type_name, 'price = 100.13')

    def test_get_price(self):
        data = {
            'login': self.test_client_login,
            'tariff': self.tariff_name,
            'service_type': self.service_type_name,
        }
        handle_action('get_domain_service_price', data)

        data = {
            'login': self.test_client_login,
            'tariff': self.tariff_name + 'fake',
            'service_type': self.service_type_name,
        }
        self.assertRaises(EmptyResultSetError, handle_action, 'get_domain_service_price', data)

        data = {
            'login': self.test_client_login,
            'tariff': self.tariff_name,
            'service_type': self.service_type_name + 'fake',
        }
        self.assertRaises(EmptyResultSetError, handle_action, 'get_domain_service_price', data)


if __name__ == '__main__':
    unittest.main()