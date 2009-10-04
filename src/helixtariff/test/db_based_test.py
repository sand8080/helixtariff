import helixtariff.test.test_environment #IGNORE:W0611 @UnusedImport

from helixcore.install import install

from helixtariff.conf.db import get_connection, transaction
from helixtariff.conf.settings import patch_table_name
from helixtariff.test.test_environment import patches_path
from helixtariff.logic.actions import handle_action
from helixtariff.logic import selector
from helixtariff.logic.handler import Handler

from root_test import RootTestCase


class DbBasedTestCase(RootTestCase):
    def setUp(self):
        install.execute('reinit', get_connection, patch_table_name, patches_path)


class ServiceTestCase(DbBasedTestCase):
    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.add_root_client()

    def add_client(self, login, password):
        handle_action('add_client', {'login': login, 'password': password})
        client = self.get_client_by_login(login)
        self.assertEqual(login, client.login)

    def add_root_client(self):
        login = Handler.root_client_stub
        self.add_client(login, 'qazwsx')

    @transaction()
    def get_client_by_login(self, login, curs=None):
        return selector.get_client_by_login(curs, login)

    def get_root_client(self):
        return self.get_client_by_login(Handler.root_client_stub)

    def add_descrs(self, service_set_desrs):
        for d in service_set_desrs:
            handle_action('add_service_set_descr', {'name': d})
            descr = self.get_service_set_descr_by_name(d)
            self.assertEqual(d, descr.name)

    @transaction()
    def get_service_type_by_name(self, client_id, name, curs=None):
        return selector.get_service_type_by_name(curs, client_id, name)

    def add_types(self, client_id, service_types):
        for t in service_types:
            handle_action('add_service_type', {'name': t})
            obj = self.get_service_type_by_name(client_id, t)
            self.assertTrue(obj.id > 0)
            self.assertEquals(obj.name, t)

    @transaction()
    def get_service_types_by_descr_name(self, name, curs=None):
        return selector.get_service_types_by_descr_name(curs, name)

    def add_to_service_set(self, name, types):
        data = {'name': name, 'types': types}
        handle_action('add_to_service_set', data)
        types = self.get_service_types_by_descr_name(data['name'])
        expected_types_names = data['types']
        self.assertEqual(len(expected_types_names), len(types))
        for idx, t in enumerate(types):
            self.assertEqual(expected_types_names[idx], t.name)

    @transaction()
    def get_service_set_descr_by_name(self, name, curs=None):
        return selector.get_service_set_descr_by_name(curs, name)

    @transaction()
    def get_tariff(self, client_id, name, curs=None):
        return selector.get_tariff(curs, client_id, name)

    def add_tariff(self, servise_set_descr, client_id, name, in_archive):
        data = {
            'service_set_descr_name': servise_set_descr,
            'client_id': client_id,
            'name': name,
            'in_archive': in_archive
        }
        handle_action('add_tariff', data)
        t = self.get_tariff(client_id, name)
        descr = self.get_service_set_descr_by_name(servise_set_descr)
        self.assertEqual(servise_set_descr, descr.name)
        self.assertEqual(descr.id, t.service_set_descr_id)
        self.assertEqual(client_id, t.client_id)
        self.assertEqual(name, t.name)

    @transaction()
    def get_rule(self, client_id, tariff_name, service_type_name, curs=None):
        return selector.get_rule(curs, client_id, tariff_name, service_type_name)

    def add_rule(self, client_id, tariff_name, service_type_name, rule):
        data = {
            'client_id': client_id,
            'tariff_name': tariff_name,
            'service_type_name': service_type_name,
            'rule': rule,
        }
        handle_action('add_rule', data)
        obj = self.get_rule(client_id, tariff_name, service_type_name)

        service_type = self.get_service_type_by_name(client_id, service_type_name)
        self.assertEqual(service_type_name, service_type.name)

        tariff = self.get_tariff(client_id, tariff_name)
        self.assertEqual(tariff_name, tariff.name)

        self.assertEqual(tariff.id, obj.tariff_id)
        self.assertEqual(service_type.id, obj.service_type_id)
        self.assertEqual(rule, obj.rule)
