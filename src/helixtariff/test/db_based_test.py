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
    def add_descrs(self, service_set_desrs):
        for d in service_set_desrs:
            handle_action('add_service_set_descr', {'name': d})

    @transaction()
    def get_service_type(self, name, curs=None):
        return selector.get_service_type_by_name(curs, name)

    def add_types(self, service_types):
        for t in service_types:
            handle_action('add_service_type', {'name': t})
            obj = self.get_service_type(t)
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

    def add_tariff(self, servise_set_descr, client_id, name):
        data = {
            'service_set_descr_name': servise_set_descr,
            'client_id': client_id,
            'name': name,
        }
        handle_action('add_tariff', data)
        t = self.get_tariff(client_id, name)
        descr = self.get_service_set_descr_by_name(servise_set_descr)
        self.assertEqual(servise_set_descr, descr.name)
        self.assertEqual(descr.id, t.service_set_descr_id)
        self.assertEqual(client_id, t.client_id)
        self.assertEqual(name, t.name)
