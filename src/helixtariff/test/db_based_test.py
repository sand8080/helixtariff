import helixtariff.test.test_environment #IGNORE:W0611 @UnusedImport

from helixcore.install import install

from helixtariff.conf.db import get_connection, transaction
from helixtariff.conf.settings import patch_table_name
from helixtariff.test.test_environment import patches_path
from helixtariff.logic.actions import handle_action
from helixtariff.logic import selector

from root_test import RootTestCase


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

    def add_service_sets(self, service_sets):
        client = self.get_client_by_login(self.test_client_login)
        for s in service_sets:
            handle_action(
                'add_service_set',
                {'login': self.test_client_login, 'password': self.test_client_password, 'name': s}
            )
            service_set = self.get_service_set_by_name(client.id, s)
            self.assertEqual(s, service_set.name)

    @transaction()
    def get_service_type_by_name(self, client_id, name, curs=None):
        return selector.get_service_type_by_name(curs, client_id, name)

    def add_types(self, service_types):
        for t in service_types:
            handle_action(
                'add_service_type',
                {'login': self.test_client_login, 'password': self.test_client_password, 'name': t}
            )
            obj = self.get_service_type_by_name(self.get_root_client().id, t)
            self.assertTrue(obj.id > 0)
            self.assertEquals(obj.name, t)

    @transaction()
    def get_service_types_by_service_set_name(self, client_id, name, curs=None):
        return selector.get_service_types_by_service_set(curs, client_id, name)

    def add_to_service_set(self, name, service_types):
        client = self.get_client_by_login(self.test_client_login)
        data = {
            'login': client.login,
            'password': self.test_client_password,
            'name': name,
            'service_types': service_types
        }
        service_types = self.get_service_types_by_service_set_name(client.id, data['name'])
        expected = set([t.name for t in service_types])
        expected.update(data['service_types'])

        handle_action('add_to_service_set', data)

        service_types = self.get_service_types_by_service_set_name(client.id, data['name'])
        actual = set([t.name for t in service_types])
        self.assertEqual(expected, actual)

    def delete_from_service_set(self, name, service_types):
        client = self.get_client_by_login(self.test_client_login)
        data = {
            'login': client.login,
            'password': self.test_client_password,
            'name': name,
            'service_types': service_types
        }
        service_types = self.get_service_types_by_service_set_name(client.id, data['name'])
        expected = set([t.name for t in service_types]).difference(data['service_types'])

        handle_action('delete_from_service_set', data)

        service_types = self.get_service_types_by_service_set_name(client.id, data['name'])
        actual = set([t.name for t in service_types])
        self.assertEqual(expected, actual)

    @transaction()
    def get_service_set_by_name(self, client_id, name, curs=None):
        return selector.get_service_set_by_name(curs, client_id, name)

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
    def get_rule(self, client_id, tariff_name, service_type_name, curs=None):
        return selector.get_rule(curs, client_id, tariff_name, service_type_name)

    def add_rule(self, tariff_name, service_type_name, rule):
        data = {
            'login': self.test_client_login,
            'password': self.test_client_password,
            'tariff': tariff_name,
            'service_type': service_type_name,
            'rule': rule,
        }
        handle_action('add_rule', data)

        client_id = self.get_root_client().id
        obj = self.get_rule(client_id, tariff_name, service_type_name)

        service_type = self.get_service_type_by_name(client_id, service_type_name)
        self.assertEqual(service_type_name, service_type.name)

        tariff = self.get_tariff(client_id, tariff_name)
        self.assertEqual(tariff_name, tariff.name)

        self.assertEqual(tariff.id, obj.tariff_id)
        self.assertEqual(service_type.id, obj.service_type_id)
        self.assertEqual(rule, obj.rule)
