import cjson

import helixtariff.test.test_environment #IGNORE:W0611 @UnusedImport

from helixcore.install import install
from helixcore.server.api import Api

from helixtariff.conf.db import get_connection, transaction
from helixtariff.conf.settings import patch_table_name
from helixtariff.test.test_environment import patches_path
from helixtariff.logic.actions import handle_action
from helixtariff.logic import selector

from root_test import RootTestCase
from helixtariff.domain.objects import Rule
from helixtariff.validator.validator import protocol
#from helixtariff.error import ObjectNotFound


class DbBasedTestCase(RootTestCase):
    def setUp(self):
        install.execute('reinit', get_connection, patch_table_name, patches_path)


class ServiceTestCase(DbBasedTestCase):
    test_login = 'test_operator'
    test_password = 'qazwsx'

    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.add_operator(self.test_login, self.test_password)

    def add_operator(self, login, password, custom_operator_info=None):
        self.handle_action('add_operator', {'login': login, 'password': password,
            'custom_operator_info': custom_operator_info})
        operator = self.get_operator_by_login(login)
        auth_client = self.get_auth_operator(login, password)
        self.assertEqual(login, operator.login)
        self.assertEqual(operator.id, auth_client.id)
        self.assertEqual(operator.login, auth_client.login)
        self.assertEqual(operator.password, auth_client.password)

    @transaction()
    def get_operator_by_login(self, login, curs=None):
        return selector.get_operator_by_login(curs, login)

    @transaction()
    def get_auth_operator(self, login, password, curs=None):
        return selector.get_auth_operator(curs, login, password)

    def add_service_sets(self, service_sets_names, service_types_names):
        operator = self.get_operator_by_login(self.test_login)
        for s in service_sets_names:
            self.handle_action('add_service_set', {'login': self.test_login,
                'password': self.test_password, 'name': s, 'service_types': service_types_names})
            service_set = self.get_service_set_by_name(operator, s)
            self.assertEqual(s, service_set.name)
            service_types = self.get_service_types_by_service_set_name(operator, service_set.name)
            st_names = [t.name for t in service_types]
            self.assertEqual(sorted(service_types_names), sorted(st_names))

    @transaction()
    def get_service_type(self, client_id, name, curs=None):
        return selector.get_service_type(curs, client_id, name)

    def add_service_types(self, service_types):
        for t in service_types:
            self.handle_action(
                'add_service_type',
                {'login': self.test_login, 'password': self.test_password, 'name': t}
            )
            operator = self.get_operator_by_login(self.test_login)
            obj = self.get_service_type(operator, t)
            self.assertTrue(obj.id > 0)
            self.assertEquals(obj.name, t)

    @transaction()
    def get_service_types_by_service_set_name(self, operator, name, curs=None):
        return selector.get_service_types_by_service_set(curs, operator, name)

    def modify_service_set(self, name, new_name=None, new_service_types=None):
        client = self.get_operator_by_login(self.test_login)
        data = {
            'login': client.login,
            'password': self.test_password,
            'name': name,
        }
        if new_name is not None:
            data['new_name'] = new_name
        if new_service_types is not None:
            data['new_service_types'] = new_service_types
        self.handle_action('modify_service_set', data)

        n = new_name if new_name else name
        service_set = self.get_service_set_by_name(client.id, n)
        service_types = self.get_service_types_by_service_set_name(client.id, service_set.name)
        actual_service_types = set([t.name for t in service_types])
        self.assertEqual(sorted(new_service_types), sorted(actual_service_types))

    @transaction()
    def get_service_set_by_name(self, operator, name, curs=None):
        return selector.get_service_set_by_name(curs, operator, name)

    @transaction()
    def get_service_set_rows(self, service_set, curs=None):
        return selector.get_service_set_rows(curs, [service_set.id])

    @transaction()
    def get_tariff(self, client_id, name, curs=None):
        return selector.get_tariff(curs, client_id, name)

    def add_tariff(self, servise_set_name, name, in_archive, parent_tariff_name):
        pass
#        client_id = self.get_root_client().id
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'service_set': servise_set_name,
#            'name': name,
#            'in_archive': in_archive,
#            'parent_tariff': parent_tariff_name
#        }
#        self.handle_action('add_tariff', data)
#        t = self.get_tariff(client_id, name)
#        parent_id = None if parent_tariff_name is None else self.get_tariff(client_id, parent_tariff_name).id
#        service_set = self.get_service_set_by_name(client_id, servise_set_name)
#        self.assertEqual(servise_set_name, service_set.name)
#        self.assertEqual(service_set.id, t.service_set_id)
#        self.assertEqual(client_id, t.client_id)
#        self.assertEqual(name, t.name)
#        self.assertEqual(parent_id, t.parent_id)
#        self.assertEqual(in_archive, t.in_archive)

    def modify_tariff(self, name, new_parent_tariff=None):
        pass
#        client_id = self.get_root_client().id
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'name': name,
#            'new_parent_tariff': new_parent_tariff
#        }
#        self.handle_action('modify_tariff', data)
#        t = self.get_tariff(client_id, name)
#        if new_parent_tariff is None:
#            parent_tariff_id = None
#        else:
#            parent_tariff_id = self.get_tariff(client_id, new_parent_tariff).id
#        self.assertEqual(name, t.name)
#        self.assertEqual(parent_tariff_id, t.parent_id)

    @transaction()
    def get_rule(self, tariff, service_type, rule_type, curs=None):
        return selector.get_rule(curs, tariff, service_type, rule_type)

    def save_draft_rule(self, tariff_name, service_type_name, rule, enabled):
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': tariff_name,
            'service_type': service_type_name,
            'rule': rule,
            'enabled': enabled,
        }
        self.handle_action('save_draft_rule', data)

        c_id = self.get_operator_by_login(self.test_login).id
        tariff = self.get_tariff(c_id, tariff_name)
        service_type = self.get_service_type(c_id, service_type_name)
        rule_type = 'draft'
        obj = self.get_rule(tariff, service_type, rule_type)

        self.assertEqual(service_type_name, service_type.name)
        self.assertEqual(tariff_name, tariff.name)
        self.assertEqual(tariff.id, obj.tariff_id)
        self.assertEqual(service_type.id, obj.service_type_id)
        self.assertEqual(rule, obj.rule)
        self.assertEqual(rule_type, obj.type)
        self.assertEqual(enabled, obj.enabled)

    @transaction()
    def get_rules(self, tariff, rule_types, curs=None):
        return selector.get_rules(curs, tariff, rule_types)

    def make_draft_rules_actual(self, tariff_name):
        client_id = self.get_operator_by_login(self.test_login).id
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'tariff': tariff_name,
        }
        self.handle_action('make_draft_rules_actual', data)
        tariff = self.get_tariff(client_id, tariff_name)
        self.assertEqual([], self.get_rules(tariff, [Rule.TYPE_DRAFT]))

    def handle_action(self, action, data):
        api = Api(protocol)
        request = dict(data, action=action)
        action_name, data = api.handle_request(cjson.encode(request))
        response = handle_action(action_name, dict(data))
        api.handle_response(action_name, dict(response))
        return response

    @transaction()
    def get_action_logs(self, client, filter_params, curs=None):
        return selector.get_action_logs(curs, client, filter_params)