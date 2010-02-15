# -*- coding: utf-8 -*-
from helixcore.server.errors import RequestProcessingError
import unittest
from random import randint
from functools import partial

from helixtariff.domain.objects import Rule
from helixtariff.error import RuleNotFound
from helixtariff.test.db_based_test import ServiceTestCase


class RuleTestCase(ServiceTestCase):
    st_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
    ss_name = 'automatic'
    t_name = u'лунный свет'

    def setUp(self):
        super(RuleTestCase, self).setUp()
        self.add_service_types(self.st_names)
        self.add_service_sets([self.ss_name], self.st_names)
        self.add_tariff(self.ss_name, self.t_name, False, None)

    def test_save_draft_rule_for_foreign_service_set(self):
        p_st_names = ['one', 'two']
        p_ss_name = 'parent set'
        p_t_name = 'parent'
        self.add_service_types(p_st_names)
        self.add_service_sets([p_ss_name], p_st_names)
        self.add_tariff(p_ss_name, p_t_name, False, None)

        ch_st_names = ['three']
        ch_ss_name = 'service set'
        ch_t_name = 'child'
        self.add_service_types(ch_st_names)
        self.add_service_sets([ch_ss_name], ch_st_names)
        self.add_tariff(ch_ss_name, ch_t_name, False, p_t_name)

        self.assertRaises(RequestProcessingError, self.save_draft_rule,
            ch_t_name, p_st_names[0], 'price = 8.00', True)

    def test_save_draft_rule(self):
        c_id = self.get_operator_by_login(self.test_login).id
        service_type = self.get_service_type(c_id, self.st_names[0])
        tariff = self.get_tariff(c_id, self.t_name)

        r_text = 'price = 1'
        enabled = False
        self.save_draft_rule(tariff.name, service_type.name, r_text, enabled)
        rule = self.get_rule(tariff, service_type, Rule.TYPE_DRAFT)
        self.assertEqual(service_type.id, rule.service_type_id)
        self.assertEqual(tariff.id, rule.tariff_id)
        self.assertEqual(r_text, rule.rule)
        self.assertEqual(enabled, rule.enabled)

        r_text = 'price = 2'
        enabled = True
        self.save_draft_rule(tariff.name, service_type.name, r_text, enabled)
        rule = self.get_rule(tariff, service_type, Rule.TYPE_DRAFT)
        self.assertEqual(service_type.id, rule.service_type_id)
        self.assertEqual(tariff.id, rule.tariff_id)
        self.assertEqual(r_text, rule.rule)
        self.assertEqual(enabled, rule.enabled)

        self.assertRaises(RequestProcessingError, self.save_draft_rule,
            tariff.name, service_type.name, 'import', True)

        self.assertRaises(RequestProcessingError, self.save_draft_rule,
            tariff.name, service_type.name, 'price = 9 ** 7', True)

        self.assertRaises(RequestProcessingError, self.save_draft_rule,
            tariff.name, service_type.name, '', True)

        self.assertRaises(RequestProcessingError, self.save_draft_rule,
            tariff.name, 'fake', 'pirce = 9', True)

        self.assertRaises(RequestProcessingError, self.save_draft_rule,
            'fake', service_type.name, 'pirce = 9', True)

        self.assertRaises(RequestProcessingError, self.save_draft_rule,
            tariff.name, service_type.name, "pirce = 9 if context['time'] else 15", True)

    def test_delete_draft_rule(self):
        c_id = self.get_operator_by_login(self.test_login).id
        service_type = self.get_service_type(c_id, self.st_names[0])
        tariff = self.get_tariff(c_id, self.t_name)

        r_text = 'price = 1'
        enabled = False
        self.save_draft_rule(tariff.name, service_type.name, r_text, enabled)
        self.get_rule(tariff, service_type, Rule.TYPE_DRAFT)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': tariff.name,
            'service_type': service_type.name,
        }
        self.handle_action('delete_draft_rule', data)
        self.assertRaises(RequestProcessingError, self.handle_action, 'delete_draft_rule', data)

    def test_make_draft_rules_actual(self):
        c_id = self.get_operator_by_login(self.test_login).id
        r_text = 'price = 1'
        st_names = self.st_names[:2]
        for st_name in st_names:
            self.save_draft_rule(self.t_name, st_name, r_text, False)
        self.make_draft_rules_actual(self.t_name)
        tariff = self.get_tariff(c_id, self.t_name)
        rule_loader = partial(self.get_rule, tariff)
        for st_name in st_names:
            service_type = self.get_service_type(c_id, st_name)
            self.assertRaises(RuleNotFound, rule_loader, service_type, Rule.TYPE_DRAFT)
            rule = rule_loader(service_type, Rule.TYPE_ACTUAL)
            self.assertEqual(service_type.id, rule.service_type_id)
            self.assertEqual(r_text, rule.rule)

        r_text = 'price = 19.00'
        enabled = True
        st_name_check = st_names[0]
        self.save_draft_rule(self.t_name, st_name_check, r_text, enabled)
        self.make_draft_rules_actual(self.t_name)

        service_type = self.get_service_type(c_id, st_name_check)
        rule = rule_loader(service_type, Rule.TYPE_ACTUAL)
        self.assertEqual(service_type.id, rule.service_type_id)
        self.assertEqual(r_text, rule.rule)
        self.assertEqual(enabled, rule.enabled)

        r_text = "price = 'lala'"
        st_name = st_names[0]
        enabled = True
        self.save_draft_rule(self.t_name, st_name, r_text, enabled)
        service_type = self.get_service_type(c_id, st_name)
        rule = rule_loader(service_type, Rule.TYPE_DRAFT)
        self.assertEqual(service_type.id, rule.service_type_id)
        self.assertEqual(r_text, rule.rule)
        self.assertEqual(enabled, rule.enabled)

        self.assertRaises(RequestProcessingError, self.make_draft_rules_actual,'fake')

    def test_modify_actual_rule(self):
        c_id = self.get_operator_by_login(self.test_login).id
        st_name = self.st_names[0]
        self.save_draft_rule(self.t_name, st_name, 'price = 1.0', True)
        self.make_draft_rules_actual(self.t_name)
        tariff = self.get_tariff(c_id, self.t_name)
        service_type = self.get_service_type(c_id, st_name)
        old_rule = self.get_rule(tariff, service_type, Rule.TYPE_ACTUAL)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
            'service_type': st_name,
            'new_enabled': False,
        }
        self.handle_action('modify_actual_rule', data)

        new_rule = self.get_rule(tariff, service_type, Rule.TYPE_ACTUAL)
        self.assertEqual(old_rule.id, new_rule.id)
        self.assertEqual(old_rule.tariff_id, new_rule.tariff_id)
        self.assertEqual(old_rule.service_type_id, new_rule.service_type_id)
        self.assertEqual(old_rule.rule, new_rule.rule)
        self.assertEqual(False, new_rule.enabled)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': 'fake',
            'service_type': st_name,
            'new_enabled': False,
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'modify_actual_rule', data)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
            'service_type': 'fake',
            'new_enabled': False,
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'modify_actual_rule', data)

    def test_get_rule(self):
        st_name = self.st_names[0]
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': 'fake %s' % self.t_name,
            'service_type': st_name,
            'type': Rule.TYPE_DRAFT,
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'get_rule', data)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
            'service_type': 'fake %s' % st_name,
            'type': Rule.TYPE_DRAFT,
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'get_rule', data)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
            'service_type': st_name,
            'type': Rule.TYPE_DRAFT,
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'get_rule', data)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
            'service_type': st_name,
            'type': Rule.TYPE_ACTUAL,
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'get_rule', data)

        r_text = 'price = 3.01'
        enabled = True
        self.save_draft_rule(self.t_name, st_name, r_text, enabled)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
            'service_type': st_name,
            'type': Rule.TYPE_DRAFT,
        }
        response = self.handle_action('get_rule', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.t_name, response['tariff'])
        self.assertEqual(st_name, response['service_type'])
        self.assertEqual(r_text, response['rule'])
        self.assertEqual(Rule.TYPE_DRAFT, response['type'])
        self.assertEqual(enabled, response['enabled'])

        self.make_draft_rules_actual(self.t_name)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
            'service_type': st_name,
            'type': Rule.TYPE_ACTUAL,
        }
        response = self.handle_action('get_rule', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.t_name, response['tariff'])
        self.assertEqual(st_name, response['service_type'])
        self.assertEqual(r_text, response['rule'])
        self.assertEqual(Rule.TYPE_ACTUAL, response['type'])
        self.assertEqual(enabled, response['enabled'])

    def test_view_rules(self):
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
        }
        response = self.handle_action('view_rules', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual([], response['rules'])

        expected_r_info = []
        for i, n in enumerate(self.st_names):
            r = 'price = %03d.%02d' % (i, i)
            enabled = randint(0, 10) % 2 == 0
            expected_r_info.append({
                'service_type': n,
                'rule': r,
                'type': Rule.TYPE_ACTUAL,
                'enabled': enabled,
            })
            self.save_draft_rule(self.t_name, n, r, enabled)
        self.make_draft_rules_actual(self.t_name)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
        }
        response = self.handle_action('view_rules', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.t_name, response['tariff'])
        self.assertEqual(expected_r_info, response['rules'])

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': 'fake',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'view_rules', data)

    def test_view_not_all_defined_rules(self):
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
        }
        response = self.handle_action('view_rules', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual([], response['rules'])

        expected_r_info = []
        for i, n in enumerate(self.st_names[1:]):
            r = 'price = %03d.%02d' % (i, i)
            enabled = randint(0, 10) % 2 == 0
            expected_r_info.append({
                'service_type': n,
                'rule': r,
                'type': Rule.TYPE_ACTUAL,
                'enabled': enabled,
            })
            self.save_draft_rule(self.t_name, n, r, enabled)
        self.make_draft_rules_actual(self.t_name)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': self.t_name,
        }
        response = self.handle_action('view_rules', data)
        self.assertEqual('ok', response['status'])
        self.assertEqual(self.t_name, response['tariff'])
        self.assertEqual(expected_r_info, response['rules'])


if __name__ == '__main__':
    unittest.main()