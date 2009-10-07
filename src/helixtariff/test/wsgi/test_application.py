import unittest
from datetime import datetime
from eventlet import api, util, wsgi, coros
import cjson
import random

from helixtariff.test.root_test import RootTestCase
from helixtariff.conf.log import logger
from helixtariff.wsgi.application import Handler
from helixtariff.test.wsgi.client import Client, random_word

util.wrap_socket_with_coroutine_socket()


class ApplicationTestCase(RootTestCase):
    class ServerLog(object):
        def write(self, s, l=0): #IGNORE:W0613
            logger.info('server: %s' % s)

    server_host = 'localhost'
    server_port = 9998

    @staticmethod
    def run_server():
        wsgi.server(
            api.tcp_listener((ApplicationTestCase.server_host, ApplicationTestCase.server_port)),
            Handler(),
            max_size=5000,
            log=ApplicationTestCase.ServerLog()
        )

    def setUp(self):
        super(ApplicationTestCase, self).setUp()
        self.cli = Client(self.server_host, self.server_port, '%s' % datetime.now(), 'qazwsx')

    def check_status_ok(self, raw_result):
        self.assertEqual('ok', cjson.decode(raw_result)['status'])

    def test_ping_ok(self):
        self.check_status_ok(self.cli.ping())

    def test_invalid_request(self):
        raw_result = self.cli.request({'action': 'fakeaction'})
        result = cjson.decode(raw_result)
        self.assertEqual('error', result['status'])
        self.assertEqual('validation', result['category'])

    def loader_task(self):
        self.cli.add_client()
        types = [random_word() for _ in range(random.randint(3, 10))]
        map(self.cli.add_service_type, types)

        descrs = [random_word() for _ in range(3)]
        map(self.cli.add_service_set_descr, descrs)

        self.cli.add_to_service_set(descrs[0], types)
        self.cli.add_to_service_set(descrs[1], types[:2])
        self.cli.add_to_service_set(descrs[2], types[1:])

        tariffs = [random_word() for _ in range(len(descrs))]
        for i, t in enumerate(tariffs):
            self.cli.add_tariff(t, descrs[i])

        # TODO: add rules
        # TODO: massive call of get functions
        # TODO: show statistics of calls

    def test_loading(self):
        pool = coros.CoroutinePool(max_size=1)

        waiters = []
        for _ in xrange(1):
            waiters.append(pool.execute_async(self.loader_task))

        for waiter in waiters:
            waiter.wait()


api.spawn(ApplicationTestCase.run_server)


if __name__ == '__main__':
    unittest.main()
