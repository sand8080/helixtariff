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
    test_client_login = 'test_client'
    test_client_password = 'qazwsx'

    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.add_root_client()

    def add_client(self, login, password):
        handle_action('add_client', {'login': login, 'password': password})
        client = self.get_client_by_login(login)
        auth_client = self.get_auth_client(login, password)
        self.assertEqual(login, client.login)
        self.assertEqual(client.id, auth_client.id)
        self.assertEqual(client.login, auth_client.login)
        self.assertEqual(client.password, auth_client.password)

    def add_root_client(self):
        self.add_client(self.test_client_login, self.test_client_password)

    @transaction()
    def get_client_by_login(self, login, curs=None):
        return selector.get_client_by_login(curs, login)

    @transaction()
    def get_auth_client(self, login, password, curs=None):
        return selector.get_auth_client(curs, login, password)

    def get_root_client(self):
        return self.get_client_by_login(self.test_client_login)

    def add_service_sets(self, service_sets_names, service_types_names):
        client = self.get_client_by_login(self.test_client_login)
        for s in service_sets_names:
            handle_action('add_service_set', {'login': self.test_client_login, 'password': self.test_client_password,
                'name': s, 'service_types': service_types_names}
            )
            service_set = self.get_service_set_by_name(client.id, s)
            self.assertEqual(s, service_set.name)
            service_types = self.get_service_types_by_service_set_name(client.id, service_set.name)
            st_names = [t.name for t in service_types]
            self.assertEqual(sorted(service_types_names), sorted(st_names))

    @transaction()
    def get_service_type(self, client_id, name, curs=None):
        return selector.get_service_type(curs, client_id, name)

    def add_service_types(self, service_types):
        for t in service_types:
            handle_action(
                'add_service_type',
                {'login': self.test_client_login, 'password': self.test_client_password, 'name': t}
            )
            obj = self.get_service_type(self.get_root_client().id, t)
            self.assertTrue(obj.id > 0)
            self.assertEquals(obj.name, t)

    @transaction()
    def get_service_types_by_service_set_name(self, client_id, name, curs=None):
        return selector.get_service_types_by_service_set(curs, client_id, name)

    def modify_service_set(self, name, new_name=None, new_service_types=None):
        client = self.get_client_by_login(self.test_client_login)
        data = {
            'login': client.login,
            'password': self.test_client_password,
            'name': name,
        }
        if new_name is not None:
            data['new_name'] = new_name
        if new_service_types is not None:
            data['new_service_types'] = new_service_types
        handle_action('modify_service_set', data)

        n = new_name if new_name else name
        service_set = self.get_service_set_by_name(client.id, n)
        service_types = self.get_service_types_by_service_set_name(client.id, service_set.name)
        actual_service_types = set([t.name for t in service_types])
        self.assertEqual(sorted(new_service_types), sorted(actual_service_types))

    @transaction()
    def get_service_set_by_name(self, client_id, name, curs=None):
        return selector.get_service_set_by_name(curs, client_id, name)

    @transaction()
    def get_service_set_rows(self, service_set, curs=None):
        return selector.get_service_set_rows(curs, [service_set.id])

    @transaction()
    def get_tariff(self, client_id, name, curs=None):
        return selector.get_tariff(curs, client_id, name)

    def add_tariff(self, servise_set_name, name, in_archive, parent_tariff_name):
        client_id = self.get_root_client().id
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'service_set': servise_set_name,
            'name': name,
            'in_archive': in_archive,
            'parent_tariff': parent_tariff_name
        }
        handle_action('add_tariff', data)
        t = self.get_tariff(client_id, name)
        parent_id = None if parent_tariff_name is None else self.get_tariff(client_id, parent_tariff_name).id
        service_set = self.get_service_set_by_name(client_id, servise_set_name)
        self.assertEqual(servise_set_name, service_set.name)
        self.assertEqual(service_set.id, t.service_set_id)
        self.assertEqual(client_id, t.client_id)
        self.assertEqual(name, t.name)
        self.assertEqual(parent_id, t.parent_id)
        self.assertEqual(in_archive, t.in_archive)

    def modify_tariff(self, name, new_parent_tariff=None):
        client_id = self.get_root_client().id
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'name': name,
            'new_parent_tariff': new_parent_tariff
        }
        handle_action('modify_tariff', data)
        t = self.get_tariff(client_id, name)
        if new_parent_tariff is None:
            parent_tariff_id = None
        else:
            parent_tariff_id = self.get_tariff(client_id, new_parent_tariff).id
        self.assertEqual(name, t.name)
        self.assertEqual(parent_tariff_id, t.parent_id)

    @transaction()
    def get_rule(self, tariff, service_type, rule_type, curs=None):
        return selector.get_rule(curs, tariff, service_type, rule_type)

    def save_draft_rule(self, tariff_name, service_type_name, rule, enabled):
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': tariff_name,
            'service_type': service_type_name,
            'rule': rule,
            'enabled': enabled,
        }
        self.handle_action('save_draft_rule', data)

        c_id = self.get_client_by_login(self.test_client_login).id
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
        client_id = self.get_client_by_login(self.test_client_login).id
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': tariff_name,
        }
        self.handle_action('make_draft_rules_actual', data)
        tariff = self.get_tariff(client_id, tariff_name)
        self.assertEqual([], self.get_rules(tariff, [Rule.TYPE_DRAFT]))

#    def delete_rule(self, tariff_name, service_type_name):
#        data = {
#            'login': self.test_client_login,
#            'password': self.test_client_password,
#            'tariff': tariff_name,
#            'service_type': service_type_name,
#        }
#        handle_action('delete_rule', data)
#
#        client_id = self.get_root_client().id
#        self.assertRaises(ObjectNotFound, self.get_rule, client_id, tariff_name, service_type_name)

    def handle_action(self, action, data):
        api = Api(protocol)
        request = dict(data, action=action)
        action_name, data = api.handle_request(cjson.encode(request))
        response = handle_action(action_name, dict(data))
        api.handle_response(action_name, dict(response))
        return response
