import unittest
from decimal import Decimal

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action
from helixtariff.error import TariffNotFound, ServiceTypeNotFound
from helixtariff.validator.validator import PRICE_CALC_NORMAL, \
    PRICE_CALC_PRICE_UNDEFINED


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

    def test_get_price(self):
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.tariff_name,
            'service_type': self.service_type_name
        }
        handle_action('delete_rule', data)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.tariff_name,
            'service_type': self.service_type_name,
        }
        response = handle_action('get_price', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.tariff_name, response['tariff'])
        self.assertEqual(self.service_type_name, response['service_type'])
        self.assertEqual([self.tariff_name], response['tariffs_chain'])
        self.assertEqual(None, response['price'])
        self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, response['price_calculation'])

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.tariff_name + 'fake',
            'service_type': self.service_type_name,
        }
        self.assertRaises(TariffNotFound, handle_action, 'get_price', data)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.tariff_name,
            'service_type': self.service_type_name + 'fake',
        }
        self.assertRaises(ServiceTypeNotFound, handle_action, 'get_price', data)

    def test_get_price_inherited(self):
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.tariff_name,
            'service_type': self.service_type_name,
        }
        response = handle_action('get_price', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.tariff_name, response['tariff'])
        self.assertEqual(self.service_type_name, response['service_type'])
        self.assertEqual([self.tariff_name], response['tariffs_chain'])
        self.assertEqual(Decimal(self.price), Decimal(response['price']))
        self.assertEqual(PRICE_CALC_NORMAL, response['price_calculation'])

        child_tariff = 'child tariff'
        child_price = '7.08'
        self.add_tariff(self.service_set_name, child_tariff, False, self.tariff_name)
        self.add_rule(child_tariff, self.service_type_name, 'price = %s' % child_price)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': child_tariff,
            'service_type': self.service_type_name,
        }
        response = handle_action('get_price', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(child_tariff, response['tariff'])
        self.assertEqual(self.service_type_name, response['service_type'])
        self.assertEqual([child_tariff], response['tariffs_chain'])
        self.assertEqual(Decimal(child_price), Decimal(response['price']))
        self.assertEqual(PRICE_CALC_NORMAL, response['price_calculation'])

        self.delete_rule(self.tariff_name, self.service_type_name)
        self.delete_rule(child_tariff, self.service_type_name)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': child_tariff,
            'service_type': self.service_type_name,
        }
        response = handle_action('get_price', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(child_tariff, response['tariff'])
        self.assertEqual(self.service_type_name, response['service_type'])
        self.assertEqual([child_tariff, self.tariff_name], response['tariffs_chain'])
        self.assertEqual(None, response['price'])
        self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, response['price_calculation'])

    def test_view_prices(self):
        expected_prices = [{
            'service_type': self.service_type_name,
            'price': self.price,
            'price_calculation': PRICE_CALC_NORMAL,
            'tariffs_chain': [self.tariff_name],
        }]
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.tariff_name,
        }
        response = handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.tariff_name, response['tariff'])
        self.assertEqual({}, response['context'])
        actual_prices = response['prices']
        self.assertEqual(len(expected_prices), len(actual_prices))
        self.assertEqual(
            self._cast(expected_prices, 'price', Decimal),
            self._cast(actual_prices, 'price', Decimal)
        )

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.tariff_name,
            'context': {'customer_id': 'c', 'period': 3},
        }
        response = handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.tariff_name, response['tariff'])
        self.assertEqual(data['context'], response['context'])
        actual_prices = response['prices']
        self.assertEqual(len(expected_prices), len(actual_prices))
        self.assertEqual(
            self._cast(expected_prices, 'price', Decimal),
            self._cast(actual_prices, 'price', Decimal)
        )

    def _cast(self, list_of_dicts, f, caster):
        result = list(list_of_dicts)
        for d in result:
            if d[f] is None:
                continue
            d[f] = caster(d[f])
        return result

    def test_child_tariff_view_prices(self):
        added_service_types = ['child service 0', 'child service 1']
        added_prices = ['10.11', '67.90']
        self.add_service_types(added_service_types)
        self.modify_service_set(self.service_set_name,
            new_service_types=[self.service_type_name] + added_service_types)
        child_tariff = 'child tariff'
        self.add_tariff(self.service_set_name, child_tariff, False, self.tariff_name)

        expected_prices = [{
            'service_type': self.service_type_name,
            'price': self.price,
            'price_calculation': PRICE_CALC_NORMAL,
            'tariffs_chain': [child_tariff, self.tariff_name],
        }]
        for i, t in enumerate(added_service_types):
            self.add_rule(child_tariff, t, 'price = %s' % added_prices[i])
            expected_prices.append({
                'service_type': t,
                'price': added_prices[i],
                'price_calculation': PRICE_CALC_NORMAL,
                'tariffs_chain': [child_tariff],
            })
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': child_tariff,
        }
        response = handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(child_tariff, response['tariff'])
        self.assertEqual({}, response['context'])
        actual_prices = response['prices']
        self.assertEqual(len(expected_prices), len(actual_prices))
        self.assertEqual(
            self._cast(expected_prices, 'price', Decimal),
            self._cast(actual_prices, 'price', Decimal)
        )

        self.delete_rule(child_tariff, added_service_types[0])
        self.delete_rule(child_tariff, added_service_types[1])
        self.add_rule(child_tariff, added_service_types[0], '''price = 1.0 if request.customer_id == 'lucky' else 11.0''')
        expected_prices = [
            {
                'service_type': self.service_type_name,
                'price': self.price,
                'price_calculation': PRICE_CALC_NORMAL,
                'tariffs_chain': [child_tariff, self.tariff_name],
            },
            {
                'service_type': added_service_types[0],
                'price': '1.0',
                'price_calculation': PRICE_CALC_NORMAL,
                'tariffs_chain': [child_tariff],
            },
            {
                'service_type': added_service_types[1],
                'price': None,
                'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
                'tariffs_chain': [child_tariff, self.tariff_name],
            },
        ]

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': child_tariff,
            'context': {'customer_id': 'lucky'},
        }
        response = handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(child_tariff, response['tariff'])
        self.assertEqual(data['context'], response['context'])
        actual_prices = response['prices']
        self.assertEqual(len(expected_prices), len(actual_prices))
        self.assertEqual(
            self._cast(expected_prices, 'price', Decimal),
            self._cast(actual_prices, 'price', Decimal)
        )

    def test_view_prices_inherited(self):
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.tariff_name,
        }
        response = handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.tariff_name, response['tariff'])
        self.assertEqual({}, response['context'])

        expected_prices = [{
            'service_type': self.service_type_name,
            'price': self.price,
            'price_calculation': PRICE_CALC_NORMAL,
            'tariffs_chain': [self.tariff_name],
        }]
        self.assertEqual(expected_prices, response['prices'])

        child_service_type = 'child service 0'
        child_service_price = '13.13'
        child_service_set = 'child service set'
        child_tariff = 'child tariff'
        self.add_service_types([child_service_type])
        self.add_service_sets([child_service_set], [child_service_type])
        self.add_tariff(child_service_set, child_tariff, False, self.tariff_name)
        self.add_rule(child_tariff, child_service_type, 'price = %s' % child_service_price)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': child_tariff,
        }
        response = handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(child_tariff, response['tariff'])
        self.assertEqual({}, response['context'])

        expected_prices = [
            {
                'service_type': self.service_type_name,
                'price': self.price,
                'tariffs_chain': [child_tariff, self.tariff_name],
            },
            {
                'service_type': child_service_type,
                'price': child_service_price,
                'tariffs_chain': [child_tariff],
            },
        ]
        self.assertEqual(len(expected_prices), len(response['prices']))
        for i, expected in enumerate(expected_prices):
            actual = response['prices'][i]
            self.assertEqual(expected['service_type'], actual['service_type'])
            self.assertEqual(expected['tariffs_chain'], actual['tariffs_chain'])
            self.assertEqual(Decimal(expected['price']), Decimal(actual['price']))

    def test_view_tariff_prices_without_rules(self):
        st_names = ['serv0', 'serv1']
        ss_name = 'set'
        t_name = 't'
        self.add_service_types(st_names)
        self.add_service_sets([ss_name], st_names)
        self.add_tariff(ss_name, t_name, False, None)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': t_name,
        }
        response = handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        prices = response['prices']
        self.assertEqual(len(st_names), len(prices))
        for p_info in prices:
            self.assertEqual(None, p_info['price'])
            self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, p_info['price_calculation'])


if __name__ == '__main__':
    unittest.main()