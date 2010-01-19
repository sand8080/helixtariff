# -*- coding: utf-8 -*-
from helixtariff.error import RuleNotFound
import unittest
from functools import partial

from helixcore.server.exceptions import DataIntegrityError

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class RuleTestCase(ServiceTestCase):
    service_types_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
    service_set_name = 'automatic'
    tariff_name = 'лунный свет'

    def setUp(self):
        super(RuleTestCase, self).setUp()
        self.add_types(self.service_types_names)
        self.add_service_sets([self.service_set_name], self.service_types_names)
        self.add_tariff(self.service_set_name, self.tariff_name, False, None)

    def test_add_rule(self):
        rule = '''
price = 100
if context.get_balance(request.customer_id) > 500: price -= 30
'''
        self.add_rule(self.tariff_name, self.service_types_names[0], rule)

    def test_add_rule_duplicate(self):
        self.add_rule(self.tariff_name, self.service_types_names[0], '')
        self.add_rule(self.tariff_name, self.service_types_names[1], '')
        self.assertRaises(DataIntegrityError, self.add_rule, self.tariff_name, self.service_types_names[1], '')

    def test_modify_rule(self):
        old_raw_rule = 'price = 10.01'
        self.add_rule(self.tariff_name, self.service_types_names[0], old_raw_rule)
        rule_loader = partial(self.get_rule, self.get_root_client().id, self.tariff_name, self.service_types_names[0])
        old_rule_obj = rule_loader()

        new_raw_rule = old_raw_rule + ' + 9.01'
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.tariff_name,
            'service_type': self.service_types_names[0],
            'new_rule': new_raw_rule
        }

        handle_action('modify_rule', data)
        new_rule_obj = rule_loader()
        self.assertEqual(old_rule_obj.id, new_rule_obj.id)
        self.assertEqual(old_rule_obj.tariff_id, new_rule_obj.tariff_id)
        self.assertEqual(old_rule_obj.service_type_id, new_rule_obj.service_type_id)
        self.assertEqual(new_raw_rule, new_rule_obj.rule)

    def test_delete_rule(self):
        self.add_rule(self.tariff_name, self.service_types_names[0], '')
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.tariff_name,
            'service_type': self.service_types_names[0]
        }
        handle_action('delete_rule', data)
        self.assertRaises(RuleNotFound, self.get_rule, self.get_root_client().id,
            self.tariff_name, self.service_types_names[0])

    def test_view_rules(self):
        client = self.get_client_by_login(self.test_client_login)
        data = {
            'login': client.login,
            'password': self.test_client_password,
            'tariff': self.tariff_name,
        }
        result = handle_action('view_rules', data)
        self.assertEqual('ok', result['status'])
        self.assertEqual([], result['rules'])

        expected_rules = []
        for i, n in enumerate(self.service_types_names):
            r = 'price = %03d.%02d' % (i, i)
            expected_rules.append({
                'service_type': n,
                'rule': r,
            })
            self.add_rule(self.tariff_name, n, r)

        data = {
            'login': client.login,
            'password': self.test_client_password,
            'tariff': self.tariff_name,
        }
        result = handle_action('view_rules', data)

        self.assertEqual('ok', result['status'])
        self.assertEqual(self.tariff_name, result['tariff'])
        self.assertEqual(expected_rules, result['rules'])

    def test_get_rule(self):
        client = self.get_client_by_login(self.test_client_login)
        data = {
            'login': client.login,
            'password': self.test_client_password,
            'tariff': self.tariff_name,
            'service_type': self.service_types_names[0],
        }
        self.assertRaises(RuleNotFound, handle_action, 'get_rule', data)

        for i, n in enumerate(self.service_types_names):
            r = 'price = %03d.%02d' % (i, i)
            self.add_rule(self.tariff_name, n, r)

            data = {
                'login': client.login,
                'password': self.test_client_password,
                'tariff': self.tariff_name,
                'service_type': n,
            }
            response = handle_action('get_rule', data)

            self.assertEqual('ok', response['status'])
            self.assertEqual(self.tariff_name, response['tariff'])
            self.assertEqual(n, response['service_type'])
            self.assertEqual(r, response['rule'])


if __name__ == '__main__':
    unittest.main()