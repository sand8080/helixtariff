from helixcore.server.errors import RequestProcessingError
import unittest
from decimal import Decimal

import helixcore.mapping.actions as mapping

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.conf.db import transaction
from helixtariff.validator.validator import PRICE_CALC_NORMAL, PRICE_CALC_PRICE_UNDEFINED
from helixtariff.domain.objects import Rule


class PriceTestCase(ServiceTestCase):
    st_name = 'register ru'
    ss_name = 'automatic'
    t_name = 'moon light'
    p_text = '100.13'
    enabled = True

    def setUp(self):
        super(PriceTestCase, self).setUp()
        self.add_service_types([self.st_name])
        self.add_service_sets([self.ss_name], [self.st_name])
        self.add_tariff(self.ss_name, self.t_name, False, None)

    def _cast(self, list_of_dicts, list_of_f, caster):
        result = list(list_of_dicts)
        for d in result:
            for f in list_of_f:
                if d[f] is None:
                    continue
                d[f] = caster(d[f])
        return result

    def test_get_price(self):
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
            'service_type': self.st_name,
        }
        response = self.handle_action('get_price', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.t_name, response['tariff'])
        self.assertEqual(self.st_name, response['service_type'])
        self.assertEqual([self.t_name], response['tariffs_chain'])
        self.assertEqual(None, response['price'])
        self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, response['price_calculation'])
        self.assertEqual([self.t_name], response['draft_tariffs_chain'])
        self.assertEqual(None, response['draft_price'])
        self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, response['draft_price_calculation'])

        data = { 'login': self.test_login, 'password': self.test_password,
            'tariff': self.t_name + 'fake', 'service_type': self.st_name}
        self.assertRaises(RequestProcessingError, self.handle_action, 'get_price', data)

        data = {'login': self.test_login, 'password': self.test_password,
            'tariff': self.t_name, 'service_type': self.st_name + 'fake'}
        self.assertRaises(RequestProcessingError, self.handle_action, 'get_price', data)

    def test_get_price_inherited(self):
        ch_t_name = 'child tariff'
        ch_t_price_text = '7.08'
        self.add_tariff(self.ss_name, ch_t_name, False, self.t_name)
        self.save_draft_rule(ch_t_name, self.st_name, 'price = %s' % ch_t_price_text, True)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': ch_t_name,
            'service_type': self.st_name,
        }
        response = self.handle_action('get_price', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(ch_t_name, response['tariff'])
        self.assertEqual(self.st_name, response['service_type'])
        self.assertEqual([ch_t_name, self.t_name], response['tariffs_chain'])
        self.assertEqual(None, response['price'])
        self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, response['price_calculation'])
        self.assertEqual([ch_t_name], response['draft_tariffs_chain'])
        self.assertEqual(Decimal(ch_t_price_text), Decimal(response['draft_price']))
        self.assertEqual(PRICE_CALC_NORMAL, response['draft_price_calculation'])

        self.make_draft_rules_actual(ch_t_name)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': ch_t_name,
            'service_type': self.st_name,
        }
        response = self.handle_action('get_price', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(ch_t_name, response['tariff'])
        self.assertEqual(self.st_name, response['service_type'])
        self.assertEqual([ch_t_name], response['tariffs_chain'])
        self.assertEqual(Decimal(ch_t_price_text), Decimal(response['price']))
        self.assertEqual(PRICE_CALC_NORMAL, response['price_calculation'])
        self.assertEqual([ch_t_name, self.t_name], response['draft_tariffs_chain'])
        self.assertEqual(None, response['draft_price'])
        self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, response['draft_price_calculation'])

    def test_view_prices(self):
        self.save_draft_rule(self.t_name, self.st_name, 'price = %s' % self.p_text, True)

        expected_prices = [{
            'service_type': self.st_name,
            'price': None,
            'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
            'tariffs_chain': [self.t_name],
            'draft_price': self.p_text,
            'draft_price_calculation': PRICE_CALC_NORMAL,
            'draft_tariffs_chain': [self.t_name],
        }]
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
        }
        response = self.handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.t_name, response['tariff'])
        self.assertEqual({}, response['context'])
        actual_prices = response['prices']
        self.assertEqual(len(expected_prices), len(actual_prices))
        self.assertEqual(
            self._cast(expected_prices, ['price', 'draft_price'], Decimal),
            self._cast(actual_prices, ['price', 'draft_price'], Decimal)
        )

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
            'context': {'customer_id': 'c', 'period': 3},
        }
        response = self.handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.t_name, response['tariff'])
        self.assertEqual(data['context'], response['context'])
        actual_prices = response['prices']
        self.assertEqual(len(expected_prices), len(actual_prices))
        self.assertEqual(
            self._cast(expected_prices, ['price', 'draft_price'], Decimal),
            self._cast(actual_prices, ['price', 'draft_price'], Decimal)
        )
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': 'fake',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'view_prices', data)

    def test_child_tariff_view_prices(self):
        added_st_names = ['child service 0', 'child service 1']
        added_p_texts = ['10.11', '67.00']
        self.add_service_types(added_st_names)
        self.modify_service_set(self.ss_name,
            new_service_types=[self.st_name] + added_st_names)
        ch_t_name = 'child tariff'
        self.add_tariff(self.ss_name, ch_t_name, False, self.t_name)

        self.save_draft_rule(self.t_name, self.st_name, 'price = %s' % self.p_text, True)
        expected_prices = [{
            'service_type': self.st_name,
            'price': None,
            'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
            'tariffs_chain': [ch_t_name, self.t_name],
            'draft_price': self.p_text,
            'draft_price_calculation': PRICE_CALC_NORMAL,
            'draft_tariffs_chain': [ch_t_name, self.t_name],
        }]
        for i, st_name in enumerate(added_st_names):
            self.save_draft_rule(ch_t_name, st_name, 'price = %s' % added_p_texts[i], True)
            expected_prices.append({
                'service_type': st_name,
                'price': None,
                'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
                'tariffs_chain': [ch_t_name, self.t_name],
                'draft_price': added_p_texts[i],
                'draft_price_calculation': PRICE_CALC_NORMAL,
                'draft_tariffs_chain': [ch_t_name],
            })
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': ch_t_name,
        }
        response = self.handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(ch_t_name, response['tariff'])
        self.assertEqual({}, response['context'])
        actual_prices = response['prices']
        self.assertEqual(len(expected_prices), len(actual_prices))
        self.assertEqual(
            self._cast(expected_prices, ['price', 'draft_price'], Decimal),
            self._cast(actual_prices, ['price', 'draft_price'], Decimal)
        )

    def test_view_prices_inherited(self):
        self.save_draft_rule(self.t_name, self.st_name, 'price = %s' % self.p_text, True)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
        }
        response = self.handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.t_name, response['tariff'])
        self.assertEqual({}, response['context'])

        expected_prices = [{
            'service_type': self.st_name,
            'price': None,
            'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
            'tariffs_chain': [self.t_name],
            'service_type': self.st_name,
            'draft_price': self.p_text,
            'draft_price_calculation': PRICE_CALC_NORMAL,
            'draft_tariffs_chain': [self.t_name],
        }]
        actual_prices = response['prices']
        self.assertEqual(
            self._cast(expected_prices, ['price', 'draft_price'], Decimal),
            self._cast(actual_prices, ['price', 'draft_price'], Decimal)
        )

        ch_st_name = 'child service 0'
        ch_p_text = '13.13'
        ch_ss_name = 'child service set'
        ch_t_name = 'child tariff'
        self.add_service_types([ch_st_name])
        self.add_service_sets([ch_ss_name], [ch_st_name])
        self.add_tariff(ch_ss_name, ch_t_name, False, self.t_name)
        self.save_draft_rule(ch_t_name, ch_st_name, 'price = %s' % ch_p_text, True)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': ch_t_name,
        }
        response = self.handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(ch_t_name, response['tariff'])
        self.assertEqual({}, response['context'])

        expected_prices = [
            {
                'service_type': self.st_name,
                'price': None,
                'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
                'tariffs_chain': [ch_t_name, self.t_name],
                'draft_price': self.p_text,
                'draft_price_calculation': PRICE_CALC_NORMAL,
                'draft_tariffs_chain': [ch_t_name, self.t_name],
            },
            {
                'service_type': ch_st_name,
                'price': None,
                'price_calculation': PRICE_CALC_PRICE_UNDEFINED,
                'tariffs_chain': [ch_t_name, self.t_name],
                'draft_price': ch_p_text,
                'draft_price_calculation': PRICE_CALC_NORMAL,
                'draft_tariffs_chain': [ch_t_name],
            },
        ]
        actual_prices = response['prices']
        self.assertEqual(len(expected_prices), len(actual_prices))
        self.assertEqual(
            self._cast(expected_prices, ['price', 'draft_price'], Decimal),
            self._cast(actual_prices, ['price', 'draft_price'], Decimal)
        )

    def test_view_tariff_prices_without_rules(self):
        st_names = ['serv0', 'serv1']
        ss_name = 'set'
        t_name = 't'
        self.add_service_types(st_names)
        self.add_service_sets([ss_name], st_names)
        self.add_tariff(ss_name, t_name, False, None)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': t_name,
        }
        response = self.handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        prices = response['prices']
        self.assertEqual(len(st_names), len(prices))
        for p_info in prices:
            self.assertEqual(None, p_info['price'])
            self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, p_info['price_calculation'])
            self.assertEqual(None, p_info['draft_price'])
            self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, p_info['draft_price_calculation'])

    @transaction()
    def _save_rule(self, rule, curs=None):
        mapping.insert(curs, rule)

    def test_view_prices_rules_unprocessed_price(self):
        st_names = ['serv0']
        ss_name = 'set'
        t_name = 't'
        self.add_service_types(st_names)
        self.add_service_sets([ss_name], st_names)
        self.add_tariff(ss_name, t_name, False, None)

        operator = self.get_operator_by_login(self.test_login)
        t_id = self.get_tariff(operator, t_name).id
        st_id = self.get_service_type(operator, st_names[0]).id
        r_text = "price = 0.0 if context.get('time') else 100"
        rule = Rule(operator_id=operator.id, type=Rule.TYPE_DRAFT, enabled=True, tariff_id=t_id,
            service_type_id=st_id, rule=r_text
        )
        self._save_rule(rule)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': t_name,
        }
        response = self.handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        p_info = response['prices'][0]
        self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, p_info['draft_price_calculation'])
        self.assertEqual(None, p_info['draft_price'])

        self.save_draft_rule(t_name, st_names[0], 'price = None', True)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': t_name,
        }
        response = self.handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        p_info = response['prices'][0]
        self.assertEqual(None, p_info['draft_price'])
        self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, p_info['draft_price_calculation'])

        self.save_draft_rule(t_name, st_names[0], "price = 'lala'", True)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': t_name,
        }
        response = self.handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        p_info = response['prices'][0]
        self.assertEqual(None, p_info['draft_price'])
        self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, p_info['draft_price_calculation'])

        price = '0.0'
        self.save_draft_rule(t_name, st_names[0], 'price = %s' % price, True)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': t_name,
        }
        response = self.handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        p_info = response['prices'][0]
        self.assertEqual(Decimal(price), Decimal(p_info['draft_price']))
        self.assertEqual(PRICE_CALC_NORMAL, p_info['draft_price_calculation'])

        price = '0.0'
        self.save_draft_rule(t_name, st_names[0], "price = %s if request['time'] else %s"
            % (price, price), True)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': t_name,
        }
        response = self.handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        p_info = response['prices'][0]
        self.assertEqual(PRICE_CALC_PRICE_UNDEFINED, p_info['draft_price_calculation'])
        self.assertEqual(None, p_info['draft_price'])

    def test_service_type_duplication(self):
        st_names = ['a', 'b', 'c', 'd']
        self.add_service_types(st_names)
        p_ss_name = 'pss'
        self.add_service_sets([p_ss_name], st_names[:3])
        p_t_name = 'p'
        self.add_tariff(p_ss_name, p_t_name, False, None)

        ch_ss_name = 'chss'
        self.add_service_sets([ch_ss_name], st_names[1:])
        ch_t_name = 'ch'
        self.add_tariff(ch_ss_name, ch_t_name, False, p_t_name)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': ch_t_name,
        }
        response = self.handle_action('view_prices', data)
        self.assertEqual('ok', response['status'])
        prices = response['prices']
        self.assertEqual(len(st_names), len(prices))


if __name__ == '__main__':
    unittest.main()