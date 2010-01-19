# coding=utf-8
import datetime
import unittest
from eventlet import api, util

from helixcore.test.util import profile
from helixcore.server.response import response_app_error
from helixcore.validol.validol import Scheme
from helixcore.server.api import Api

from helixtariff.test.db_based_test import DbBasedTestCase
from helixtariff.test.wsgi.client import Client
from helixtariff.wsgi.server import Server
from helixtariff.validator.validator import protocol, ApiCall, RESPONSE_STATUS_ERROR
from helixtariff.logic.handler import Handler

util.wrap_socket_with_coroutine_socket()

api.spawn(Server.run)


class NginxTestCase(DbBasedTestCase):
    nginx_host = 'localhost'
    nginx_port = 1053

    def setUp(self):
        super(NginxTestCase, self).setUp()
        self.cli = Client(self.nginx_host, self.nginx_port, '%s' % datetime.datetime.now(),
            'qazwsx', protocol='https')

    def check_status_ok(self, response):
        self.assertEqual('ok', response['status'])

    def ping(self):
        return self.cli.ping() #IGNORE:E1101

    @profile
    def ping_loading(self, repeats=1): #IGNORE:W0613
        self.ping()

    def test_ping_ok(self):
        self.check_status_ok(self.ping())
        self.ping_loading(repeats=50)

    def test_get_empty_service_types(self):
        self.cli.add_client(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
        self.check_status_ok(
            self.cli.view_service_types(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
        )

    def test_invalid_request(self):
        response = self.cli.request({'action': 'fakeaction'})
        self.assertEqual('error', response['status'])
        self.assertEqual('validation', response['category'])

    def test_service_set(self):
        login = u'перес'
        password = 'qazwsx'
        service_type = u'помощь зала'
        service_set = u'программа помощи малому бизнесу'
        self.cli.request({'action': 'add_client', 'login': login, 'password': password})
        self.cli.request({'action': 'add_service_type', 'login': login, 'password': password,
            'name': service_type})
        self.cli.request({'action': 'add_service_set', 'login': login, 'password': password,
            'name': service_set, 'service_types': [service_type]})
        self.cli.request({'action': 'get_service_set', 'login': login, 'password': password,
            'name': service_set})
        self.cli.request({'action': 'view_service_sets', 'login': login, 'password': password})

    def test_unicode(self):
        login = u'василий'
        password = 'qazwsx'
        response = self.cli.request({'action': 'add_client', 'login': login, 'password': password})
        self.check_status_ok(response)
        response = self.cli.request({'action': 'view_service_types', 'login': login, 'password': password})
        self.check_status_ok(response)

    def test_bytestr(self):
        a = Api(protocol)
        handler = Handler()
        request = '{"action": "add_client", "password": "f", "login": "c"}'
        _, decoded_data = a.handle_request(request)
        handler.add_client(decoded_data)

        request = '{"action": "add_service_type", "login": "c", "password": "f", "name": "\u0447\u0447\u0447"}'
        _, decoded_data = a.handle_request(request)
        handler.add_service_type(decoded_data)

        request = '{"action": "view_service_types", "login": "c", "password": "f"}'
        _, decoded_data = a.handle_request(request)
        response = handler.view_service_types(decoded_data)
        self.assertEqual([u'\u0447\u0447\u0447'], response['service_types'])

    def test_number_in_error_message(self):
        global protocol #IGNORE:W0603
        def incorect_error_message(self, _): #IGNORE:W0613
            return response_app_error(1)
        Handler.incorect_error_message = incorect_error_message
        protocol += [
            ApiCall('incorect_error_message_request', Scheme({})),
            ApiCall('incorect_error_message_response', Scheme(RESPONSE_STATUS_ERROR)),
        ]
        cli = Client(self.nginx_host, self.nginx_port, 'cli0', 'qazwsx', protocol='https')
        response = cli.incorect_error_message() #IGNORE:E1101
        self.assertEqual('error', response['status'])
        self.assertEqual('validation', response['category'])


if __name__ == '__main__':
    unittest.main()
