import unittest

from helixcore.db.wrapper import EmptyResultSetError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action
from helixtariff.error import TariffCycleError, NoRuleFound


class DomainPriceTestCase(ServiceTestCase):
    service_type_name = 'register ru'
    service_set_name = 'automatic'
    tariff_name = 'moon light'

    def setUp(self):
        super(DomainPriceTestCase, self).setUp()
        self.add_service_sets([self.service_set_name])
        self.add_types([self.service_type_name])
        self.add_to_service_set(self.service_set_name, [self.service_type_name])
        self.add_tariff(self.service_set_name, self.tariff_name, False, None)
        self.add_rule(self.tariff_name, self.service_type_name, 'price = 100.13')

    def test_tariffs_cycle(self):
        tariff_0 = 'tariff 0'
        self.add_tariff(self.service_set_name, tariff_0, False, None)
        tariff_1 = 'tariff 1'
        self.add_tariff(self.service_set_name, tariff_1, False, tariff_0)
        tariff_2 = 'tariff 2'
        self.add_tariff(self.service_set_name, tariff_2, False, tariff_0)
        self.modify_tariff(tariff_0, tariff_2)
        data = {
            'login': self.test_client_login,
            'tariff': tariff_2,
            'service_type': self.service_type_name,
        }
        self.assertRaises(TariffCycleError, handle_action, 'get_domain_service_price', data)

    def test_no_rule_found(self):
        tariff_0 = 'tariff 0'
        self.add_tariff(self.service_set_name, tariff_0, False, None)
        tariff_1 = 'tariff 1'
        self.add_tariff(self.service_set_name, tariff_1, False, tariff_0)
        tariff_2 = 'tariff 2'
        self.add_tariff(self.service_set_name, tariff_2, False, tariff_0)
        self.modify_tariff(self.tariff_name, tariff_1)
        data = {
            'login': self.test_client_login,
            'tariff': tariff_2,
            'service_type': self.service_type_name,
        }
        self.assertRaises(NoRuleFound, handle_action, 'get_domain_service_price', data)

    def test_get_price(self):
        data = {
            'login': self.test_client_login,
            'tariff': self.tariff_name,
            'service_type': self.service_type_name,
        }
        response = handle_action('get_domain_service_price', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.tariff_name, response['tariff'])
        self.assertEqual(self.service_type_name, response['service_type'])
        self.assertEqual([self.tariff_name], response['tariffs_chain'])

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
        self.assertRaises(NoRuleFound, handle_action, 'get_domain_service_price', data)


if __name__ == '__main__':
    unittest.main()