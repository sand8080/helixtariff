# coding=utf-8
import unittest
import datetime

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.conf import settings
from helixtariff.test.test_environment import start_server

from helixtariff.test.wsgi.client import Client


class ActionLogTestCase(ServiceTestCase):
    def setUp(self):
        super(ActionLogTestCase, self).setUp()
        self.cli = Client(settings.server_host, settings.server_port,
            u'егор %s' % datetime.datetime.now(), 'qazwsx')

    def _check_action_tracked(self, client, action_name, source):
        action_logs = self.get_action_logs(client, {'action': action_name})
        self.assertEqual(1, len(action_logs))
        action_log = action_logs[0]
        self.assertEqual(client.id, action_log.client_id)
        self.assertEqual(action_name, action_log.action)
        self.assertEqual(source, action_log.source)

    def _make_trackable_action(self, client, action_name, data):
        auth_data = {'login': self.cli.login, 'password': self.cli.password}
        auth_data.update(data)
        m = getattr(self.cli, action_name)
        m(**auth_data)
        self._check_action_tracked(client, action_name, data.get('source', None))

    def test_unauthorized_tracking_action(self):
        self.cli.add_client(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
        self._check_action_tracked(self.get_client_by_login(self.cli.login), 'add_client', None)

    def test_tracking_error_action(self):
        source = 'fake'
        self.cli.add_client(login=self.cli.login, password=self.cli.password, source=source) #IGNORE:E1101
        client = self.get_client_by_login(self.cli.login)
        self._check_action_tracked(client, 'add_client', source)
        self._make_trackable_action(client, 'modify_service_type', {'name': 'fake', 'new_name': 'ff'})

    def test_tracking_action(self):
        self.cli.add_client(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
        client = self.get_client_by_login(self.cli.login)

        self._make_trackable_action(client, 'modify_client', {'source': 'jah'})

        old_st_name = 'service type'
        self._make_trackable_action(client, 'add_service_type', {'name': old_st_name})
        st_name = 'new %s' % old_st_name
        self._make_trackable_action(client, 'modify_service_type', {'name': old_st_name,
            'new_name': st_name})

        old_ss_name = 'service set'
        self._make_trackable_action(client, 'add_service_set', {'name': old_ss_name,
            'service_types': [st_name]})
        ss_name = 'new %s' % old_ss_name
        self._make_trackable_action(client, 'modify_service_set', {'name': old_ss_name,
            'new_name': ss_name})

        old_t_name = 'tariff'
        self._make_trackable_action(client, 'add_tariff', {'name': old_t_name,
            'parent_tariff': None, 'service_set': ss_name, 'in_archive': False})
        t_name = 'new %s' % old_t_name
        self._make_trackable_action(client, 'modify_tariff', {'name': old_t_name,
            'new_name': t_name, 'new_in_archive': True})

        r_text = 'price = 1.0'
        self._make_trackable_action(client, 'save_draft_rule', {'tariff': t_name,
            'service_type': st_name, 'rule': r_text, 'enabled': True})
        self._make_trackable_action(client, 'make_draft_rules_actual', {'tariff': t_name})
        self._make_trackable_action(client, 'modify_actual_rule', {'tariff': t_name,
            'service_type': st_name, 'new_enabled': False})

        self._make_trackable_action(client, 'delete_tariff', {'name': t_name})
        self.cli.modify_service_set(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
            name=ss_name, new_service_types=[])
        self._make_trackable_action(client, 'delete_service_set', {'name': ss_name})
        self._make_trackable_action(client, 'delete_service_type', {'name': st_name})


if __name__ == '__main__':
    start_server()
    unittest.main()
