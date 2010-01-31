# coding=utf-8
from eventlet import api, util
util.wrap_socket_with_coroutine_socket()

import unittest
import datetime

from helixtariff.test.db_based_test import ServiceTestCase
from helixtariff.conf import settings
from helixtariff.test.wsgi.client import Client
from helixtariff.wsgi.server import Server


api.spawn(Server.run)


class ActionLogTestCase(ServiceTestCase):
    def setUp(self):
        super(ActionLogTestCase, self).setUp()
        self.cli = Client(settings.server_host, settings.server_port,
            u'егор %s' % datetime.datetime.now(), 'qazwsx')

    def test_unauthorized_tracking_action(self):
        self.cli.add_client(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
        self._check_action_tracked(self.get_client_by_login(self.cli.login), 'add_client')

    def test_tracking_error_action(self):
        self.cli.add_client(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
        client = self.get_client_by_login(self.cli.login)
        self._check_action_tracked(client, 'add_client')
        self._make_trackable_action(client, 'modify_service_type', {'name': 'fake', 'new_name': 'ff'})

    def _check_action_tracked(self, client, action_name):
        action_logs = self.get_action_logs(client, {'action': action_name})
        self.assertEqual(1, len(action_logs))
        action_log = action_logs[0]
        self.assertEqual(client.id, action_log.client_id)
        self.assertEqual(action_name, action_log.action)

    def _make_trackable_action(self, client, action_name, data):
        auth_data = {'login': self.cli.login, 'password': self.cli.password}
        auth_data.update(data)
        m = getattr(self.cli, action_name)
        m(**auth_data)
        self._check_action_tracked(client, action_name)

    def test_tracking_action(self):
        self.cli.add_client(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
        client = self.get_client_by_login(self.cli.login)

        self._make_trackable_action(client, 'modify_client', {})

        st_name = 'service type'
        self._make_trackable_action(client, 'add_service_type', {'name': st_name})
        self._make_trackable_action(client, 'modify_service_type', {'name': st_name,
            'new_name': 'new %s' % st_name})
        self._make_trackable_action(client, 'delete_service_type', {'name': 'new %s' % st_name})


if __name__ == '__main__':
    unittest.main()
