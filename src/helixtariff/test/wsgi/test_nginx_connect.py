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


if __name__ == '__main__':
    unittest.main()