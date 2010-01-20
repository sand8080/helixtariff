import unittest
from decimal import Decimal

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action
from helixtariff.error import RuleNotFound, TariffNotFound


class PriceTestCase(ServiceTestCase):
    service_type_name = 'register ru'
    service_set_name = 'automatic'
    tariff_name = 'moon light'
    price = '100.13'

    def setUp(self):
        super(PriceTestCase, self).setUp()
        self.add_service_types([self.service_type_name])
        self.add_service_sets([self.service_set_name], [self.service_type_name])
        self.add_tariff(self.service_set_name, self.tariff_name, False, None)
        self.add_rule(self.tariff_name, self.service_type_name, 'price = %s' % self.price)

#    def test_no_rule_found(self):
#        tariff_0 = 'tariff 0'
#        self.add_tariff(self.service_set_name, tariff_0, False, None)
#        tariff_1 = 'tariff 1'
#        self.add_tariff(self.service_set_name, tariff_1, False, tariff_0)
#        tariff_2 = 'tariff 2'
#        self.add_tariff(self.service_set_name, tariff_2, False, tariff_0)
#        self.modify_tariff(self.tariff_name, tariff_1)
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': tariff_2,
#            'service_type': self.service_type_name,
#        }
#        self.assertRaises(RuleNotFound, handle_action, 'get_price', data)
#
#    def test_get_price(self):
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#            'service_type': self.service_type_name,
#        }
#        response = handle_action('get_price', data)
#        self.assertEqual('ok', response['status'])
#        self.assertEqual(self.tariff_name, response['tariff'])
#        self.assertEqual(self.service_type_name, response['service_type'])
#        self.assertEqual([self.tariff_name], response['tariffs_chain'])
#        self.assertEqual(Decimal(self.price), Decimal(response['price']))
#
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name + 'fake',
#            'service_type': self.service_type_name,
#        }
#        self.assertRaises(TariffNotFound, handle_action, 'get_price', data)
#
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#            'service_type': self.service_type_name + 'fake',
#        }
#        self.assertRaises(RuleNotFound, handle_action, 'get_price', data)
#
#    def test_get_price_inherited(self):
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#            'service_type': self.service_type_name,
#        }
#        response = handle_action('get_price', data)
#        self.assertEqual('ok', response['status'])
#        self.assertEqual(self.tariff_name, response['tariff'])
#        self.assertEqual(self.service_type_name, response['service_type'])
#        self.assertEqual([self.tariff_name], response['tariffs_chain'])
#        self.assertEqual(Decimal(self.price), Decimal(response['price']))
#
#        child_tariff = 'child tariff'
#        child_price = '7.08'
#        self.add_tariff(self.service_set_name, child_tariff, False, self.tariff_name)
#        self.add_rule(child_tariff, self.service_type_name, 'price = %s' % child_price)
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': child_tariff,
#            'service_type': self.service_type_name,
#        }
#        response = handle_action('get_price', data)
#        self.assertEqual('ok', response['status'])
#        self.assertEqual(child_tariff, response['tariff'])
#        self.assertEqual(self.service_type_name, response['service_type'])
#        self.assertEqual([child_tariff], response['tariffs_chain'])
#        self.assertEqual(Decimal(child_price), Decimal(response['price']))
#
#    def test_view_prices(self):
#        expected_prices = [{
#            'service_type': self.service_type_name,
#            'price': self.price,
#            'tariffs_chain': [self.tariff_name],
#        }]
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#        }
#        response = handle_action('view_prices', data)
#        self.assertEqual('ok', response['status'])
#        self.assertEqual(self.tariff_name, response['tariff'])
#        self.assertEqual({}, response['context'])
#        self.assertEqual(expected_prices, response['prices'])
#
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#            'context': {'customer_id': 'c', 'period': 3},
#        }
#        response = handle_action('view_prices', data)
#        self.assertEqual('ok', response['status'])
#        self.assertEqual(self.tariff_name, response['tariff'])
#        self.assertEqual(data['context'], response['context'])
#        self.assertEqual(len(expected_prices), len(response['prices']))
#        for i, expected in enumerate(expected_prices):
#            actual = response['prices'][i]
#            self.assertEqual(expected['service_type'], actual['service_type'])
#            self.assertEqual(expected['tariffs_chain'], actual['tariffs_chain'])
#            self.assertEqual(Decimal(expected['price']), Decimal(actual['price']))
#
#    def test_child_tariff_view_prices(self):
#        added_service_types = ['child service 0', 'child service 1']
#        added_prices = ['10.11', '67.90']
#        self.add_service_types(added_service_types)
#        self.modify_service_set(self.service_set_name,
#            new_service_types=[self.service_type_name] + added_service_types)
#        child_tariff = 'child tariff'
#        self.add_tariff(self.service_set_name, child_tariff, False, self.tariff_name)
#
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#            'service_type': self.service_type_name
#        }
#        price_info = handle_action('get_price', data)
#
#        expected_prices = [{
#            'service_type': price_info['service_type'],
#            'price': price_info['price'],
#            'tariffs_chain': price_info['tariffs_chain'],
#        }]
#        for i, t in enumerate(added_service_types):
#            self.add_rule(child_tariff, t, 'price = %s' % added_prices[i])
#            expected_prices.append({
#                'service_type': t,
#                'price': added_prices[i],
#                'tariffs_chain': [child_tariff],
#            })
#        print expected_prices
#
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#        }
#        response = handle_action('view_prices', data)
#        self.assertEqual('ok', response['status'])
#        self.assertEqual(self.tariff_name, response['tariff'])
#        self.assertEqual({}, response['context'])
#        self.assertEqual(expected_prices, response['prices'])


#        self.add_rule(child_tariff, types[0], "price = %s if request.customer_id == 'lucky' else %s" % ('1.0', self.price))
#
#        expected_prices = [
#            {
#                'service_type': self.service_type_name,
#                'price': self.price,
#                'tariffs_chain': [child_tariff, self.tariff_name],
#            },
#            {
#                'service_type': types[0],
#                'price': '1.0',
#                'tariffs_chain': [child_tariff],
#            }
#        ]
#
#        for i, t in enumerate(types[1:]):
#            self.add_rule(child_tariff, t, 'price = %s' % prices[i])
#            expected_prices.append({
#                'service_type': t,
#                'price': prices[i],
#                'tariffs_chain': [child_tariff],
#            })
#
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': child_tariff,
#            'context': {'customer_id': 'lucky'},
#        }
#        response = handle_action('view_prices', data)
#        print '###', response
#        self.assertEqual('ok', response['status'])
#        self.assertEqual(child_tariff, response['tariff'])
#        self.assertEqual(data['context'], response['context'])
#        self.assertEqual(len(expected_prices), len(response['prices']))
#        for i, expected in enumerate(expected_prices):
#            actual = response['prices'][i]
#            self.assertEqual(expected['service_type'], actual['service_type'])
#            self.assertEqual(expected['tariffs_chain'], actual['tariffs_chain'])
#            self.assertEqual(Decimal(expected['price']), Decimal(actual['price']))

#    def test_view_prices_inherited(self):
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#        }
#        response = handle_action('view_prices', data)
#        self.assertEqual('ok', response['status'])
#        self.assertEqual(self.tariff_name, response['tariff'])
#        self.assertEqual({}, response['context'])
#
#        expected_prices = [{
#            'service_type': self.service_type_name,
#            'price': self.price,
#            'tariffs_chain': [self.tariff_name],
#        }]
#        self.assertEqual(expected_prices, response['prices'])
#
#        child_service_type = 'child service 0'
#        child_service_price = '13.13'
#        child_service_set = 'child service set'
#        child_tariff = 'child tariff'
#        self.add_service_types([child_service_type])
#        self.add_service_sets([child_service_set], [child_service_type])
#        self.add_tariff(child_service_set, child_tariff, False, self.tariff_name)
#        self.add_rule(child_tariff, child_service_type, 'price = %s' % child_service_price)
#
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': child_tariff,
#        }
#        response = handle_action('view_prices', data)
#        self.assertEqual('ok', response['status'])
#        self.assertEqual(child_tariff, response['tariff'])
#        self.assertEqual({}, response['context'])
#
#        expected_prices = [
#            {
#                'service_type': self.service_type_name,
#                'price': self.price,
#                'tariffs_chain': [child_tariff, self.tariff_name],
#            },
#            {
#                'service_type': child_service_type,
#                'price': child_service_price,
#                'tariffs_chain': [child_tariff],
#            },
#        ]
#        self.assertEqual(len(expected_prices), len(response['prices']))
#        for i, expected in enumerate(expected_prices):
#            actual = response['prices'][i]
#            self.assertEqual(expected['service_type'], actual['service_type'])
#            self.assertEqual(expected['tariffs_chain'], actual['tariffs_chain'])
#            self.assertEqual(Decimal(expected['price']), Decimal(actual['price']))
#
#    def test_view_prices_without_rule(self):
#        new_service_type = 'new service'
#        self.add_service_types([new_service_type])
#        self.modify_service_set(self.service_set_name, new_service_types=[new_service_type])
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#        }
#        self.assertRaises(RuleNotFound, handle_action, 'view_prices', data)


if __name__ == '__main__':
    unittest.main()