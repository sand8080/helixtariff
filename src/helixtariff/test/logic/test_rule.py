# -*- coding: utf-8 -*-
import unittest
from functools import partial

from helixcore.db.wrapper import ObjectAlreadyExists

from helixtariff.domain.objects import Rule
from helixtariff.error import RuleNotFound, TariffNotFound, ServiceTypeNotFound
from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.logic.actions import handle_action


class RuleTestCase(ServiceTestCase):
    st_names = ['register ru', 'prolong ru', 'register hn', 'prolong hn']
    ss_name = 'automatic'
    t_name = u'лунный свет'

    def setUp(self):
        super(RuleTestCase, self).setUp()
        self.add_service_types(self.st_names)
        self.add_service_sets([self.ss_name], self.st_names)
        self.add_tariff(self.ss_name, self.t_name, False, None)

    def test_save_draft_rule(self):
        c_id = self.get_client_by_login(self.test_client_login).id
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

    def test_make_draft_rules_actual(self):
        c_id = self.get_client_by_login(self.test_client_login).id
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

    def test_modify_actual_rule(self):
        c_id = self.get_client_by_login(self.test_client_login).id
        st_name = self.st_names[0]
        self.save_draft_rule(self.t_name, st_name, '', True)
        self.make_draft_rules_actual(self.t_name)
        tariff = self.get_tariff(c_id, self.t_name)
        service_type = self.get_service_type(c_id, st_name)
        old_rule = self.get_rule(tariff, service_type, Rule.TYPE_ACTUAL)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
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

    def test_get_rule(self):
        c_id = self.get_client_by_login(self.test_client_login).id
        st_name = self.st_names[0]
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': 'fake %s' % self.t_name,
            'service_type': st_name,
            'type': Rule.TYPE_DRAFT,
        }
        self.assertRaises(TariffNotFound, handle_action, 'get_rule', data)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.t_name,
            'service_type': 'fake %s' % st_name,
            'type': Rule.TYPE_DRAFT,
        }
        self.assertRaises(ServiceTypeNotFound, handle_action, 'get_rule', data)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.t_name,
            'service_type': st_name,
            'type': Rule.TYPE_DRAFT,
        }
        self.assertRaises(RuleNotFound, handle_action, 'get_rule', data)
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': self.t_name,
            'service_type': st_name,
            'type': Rule.TYPE_ACTUAL,
        }
        self.assertRaises(RuleNotFound, handle_action, 'get_rule', data)

        r_text = 'price = 3.01'
        enabled = True
        self.save_draft_rule(self.t_name, st_name, r_text, enabled)

        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
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
            'login': self.test_client_login,
            'password': self.test_client_password,
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


#    def test_modify_rule(self):
#        old_raw_rule = 'price = 10.01'
#        self.add_rule(self.tariff_name, self.service_types_names[0], old_raw_rule)
#        rule_loader = partial(self.get_rule, self.get_root_client().id, self.tariff_name, self.service_types_names[0])
#        old_rule_obj = rule_loader()
#
#        new_raw_rule = old_raw_rule + ' + 9.01'
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#            'service_type': self.service_types_names[0],
#            'new_rule': new_raw_rule
#        }
#
#        handle_action('modify_rule', data)
#        new_rule_obj = rule_loader()
#        self.assertEqual(old_rule_obj.id, new_rule_obj.id)
#        self.assertEqual(old_rule_obj.tariff_id, new_rule_obj.tariff_id)
#        self.assertEqual(old_rule_obj.service_type_id, new_rule_obj.service_type_id)
#        self.assertEqual(new_raw_rule, new_rule_obj.rule)
#
#    def test_delete_rule(self):
#        self.add_rule(self.tariff_name, self.service_types_names[0], '')
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#            'service_type': self.service_types_names[0]
#        }
#        handle_action('delete_rule', data)
#        self.assertRaises(RuleNotFound, self.get_rule, self.get_root_client().id,
#            self.tariff_name, self.service_types_names[0])
#
#    def test_view_rules(self):
#        client = self.get_client_by_login(self.test_client_login)
#        data = {
#            'login': client.login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#        }
#        result = handle_action('view_rules', data)
#        self.assertEqual('ok', result['status'])
#        self.assertEqual([], result['rules'])
#
#        expected_rules = []
#        for i, n in enumerate(self.service_types_names):
#            r = 'price = %03d.%02d' % (i, i)
#            expected_rules.append({
#                'service_type': n,
#                'rule': r,
#            })
#            self.add_rule(self.tariff_name, n, r)
#
#        data = {
#            'login': client.login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#        }
#        result = handle_action('view_rules', data)
#
#        self.assertEqual('ok', result['status'])
#        self.assertEqual(self.tariff_name, result['tariff'])
#        self.assertEqual(expected_rules, result['rules'])
#
#    def test_view_not_all_defined_rules(self):
#        client = self.get_client_by_login(self.test_client_login)
#        data = {
#            'login': client.login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#        }
#        response = handle_action('view_rules', data)
#        self.assertEqual('ok', response['status'])
#        self.assertEqual([], response['rules'])
#
#        expected_rules = []
#        for i, n in enumerate(self.service_types_names[1:]):
#            r = 'price = %03d.%02d' % (i, i)
#            expected_rules.append({
#                'service_type': n,
#                'rule': r,
#            })
#            self.add_rule(self.tariff_name, n, r)
#
#        data = {
#            'login': client.login,
#            'password': self.test_client_password,
#            'tariff': self.tariff_name,
#        }
#        response = handle_action('view_rules', data)
#        self.assertEqual('ok', response['status'])
#        self.assertEqual(self.tariff_name, response['tariff'])
#        self.assertEqual(expected_rules, response['rules'])
#


if __name__ == '__main__':
    unittest.main()