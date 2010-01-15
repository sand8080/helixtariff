# coding=utf-8
import datetime
import cjson
import unittest
from eventlet import api, util

from helixcore.test.util import profile

from helixtariff.test.db_based_test import DbBasedTestCase
from helixtariff.test.wsgi.client import Client
from helixtariff.wsgi.server import Server

util.wrap_socket_with_coroutine_socket()

api.spawn(Server.run)

from helixcore.server.api import Api
from helixtariff.validator.validator import protocol
from helixtariff.logic.handler import Handler

class NginxTestCase(DbBasedTestCase):
    nginx_host = 'localhost'
    nginx_port = 1053

    def setUp(self):
        super(NginxTestCase, self).setUp()
        self.cli = Client(self.nginx_host, self.nginx_port, '%s' % datetime.datetime.now(),
            'qazwsx', protocol='https')

    def check_status_ok(self, raw_result):
        self.assertEqual('ok', cjson.decode(raw_result)['status'])

    def ping(self):
        return self.cli.ping()

    @profile
    def ping_loading(self, repeats=1): #IGNORE:W0613
        self.ping()

    def test_ping_ok(self):
        self.check_status_ok(self.ping())
        self.ping_loading(repeats=50)

    def test_get_empty_service_types(self):
        raw_result = self.cli.get_service_types()
        result = cjson.decode(raw_result)
        self.assertEqual('error', result['status'])
        self.cli.add_client()
        self.check_status_ok(self.cli.get_service_types())

    def test_invalid_request(self):
        raw_result = self.cli.request({'action': 'fakeaction'})
        result = cjson.decode(raw_result)
        self.assertEqual('error', result['status'])
        self.assertEqual('validation', result['category'])

    def test_service_set(self):
        login = u'перес'
        password = 'qazwsx'
        service_type = u'помощь зала'
        service_set = u'программа помощи малому бизнесу'
        self.cli.request({'action': 'add_client', 'login': login, 'password': password})
        self.cli.request({'action': 'add_service_type', 'login': login, 'password': password,
            'name': service_type})
        self.cli.request({'action': 'add_service_set', 'login': login, 'password': password,
            'name': service_set})
        self.cli.request({'action': 'add_to_service_set', 'login': login, 'password': password,
            'name': service_set, 'types': [service_type]})
        self.cli.request({'action': 'get_service_set', 'login': login, 'password': password,
            'name': service_set})
        self.cli.request({'action': 'view_service_sets', 'login': login, 'password': password})

    def test_unicode(self):
        login = u'василий'
        password = 'qazwsx'
        self.cli.request({'action': 'add_client', 'login': login, 'password': password})
        self.cli.request({'action': 'get_service_types', 'login': login, 'password': password})

    def test_bytestr(self):
        a = Api(protocol)
        handler = Handler()
        request = '{"action": "add_client", "password": "f", "login": "c"}'
        _, decoded_data = a.handle_request(request)
        handler.add_client(decoded_data)

        request = '{"action": "add_service_type", "login": "c", "password": "f", "name": "\u0447\u0447\u0447"}'
        _, decoded_data = a.handle_request(request)
        handler.add_service_type(decoded_data)

        request = '{"action": "get_service_types", "login": "c", "password": "f"}'
        _, decoded_data = a.handle_request(request)
        response = handler.get_service_types(decoded_data)
        self.assertEqual(response['types'], [u'\u0447\u0447\u0447'])


if __name__ == '__main__':
    unittest.main()
