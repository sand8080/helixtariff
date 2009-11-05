#import cProfile

from decimal import Decimal
import unittest
import datetime
from eventlet import api, util, coros
import cjson
import random

from helixcore.test.util import random_word, select_random, profile

from helixtariff.test.db_based_test import DbBasedTestCase
from helixtariff.conf import settings
from helixtariff.test.wsgi.client import Client
from helixtariff.wsgi.server import Server

util.wrap_socket_with_coroutine_socket()

api.spawn(Server.run)


class ApplicationTestCase(DbBasedTestCase):
    def setUp(self):
        super(ApplicationTestCase, self).setUp()
        self.cli = Client(settings.server_host, settings.server_port, '%s' % datetime.datetime.now(), 'qazwsx')

    def check_status_ok(self, raw_result):
        self.assertEqual('ok', cjson.decode(raw_result)['status'])

    def test_ping_ok(self):
        self.check_status_ok(self.cli.ping())

    def test_invalid_request(self):
        raw_result = self.cli.request({'action': 'fakeaction'})
        result = cjson.decode(raw_result)
        self.assertEqual('error', result['status'])
        self.assertEqual('validation', result['category'])


    def load_detailed_tariff_data(self, tariffs_names):
        tariffs = {}
        for n in tariffs_names:
            tariffs[n] = self.cli.get_tariff_detailed(n)
        return tariffs

    @profile
    def get_tariff_detailed(self, tariffs_names, repeats=1): #IGNORE:W0613
        tariff_name = select_random(tariffs_names)
        return self.cli.get_tariff_detailed(tariff_name)

    @profile
    def get_price(self, tariffs_detailed, repeats=1): #IGNORE:W0613
        tariff_name = select_random(tariffs_detailed.keys())
        service_types_names = tariffs_detailed[tariff_name]['types']
        return self.cli.get_price(tariff_name, select_random(service_types_names))

    @profile
    def get_wrong_price(self, tariffs_detailed, repeats=1): #IGNORE:W0613
        tariff_name = select_random(tariffs_detailed.keys())
        service_types_names = tariffs_detailed[tariff_name]['types']
        return self.cli.get_price(tariff_name, select_random(service_types_names) + 'fake')

    def loader_task(self):
        types = [random_word() for _ in range(random.randint(3, 10))]
        map(self.cli.add_service_type, types)

        descrs = [random_word() for _ in range(3)]
        map(self.cli.add_service_set_descr, descrs)

        self.cli.add_to_service_set(descrs[0], types)
        self.cli.add_to_service_set(descrs[1], types[:2])
        self.cli.add_to_service_set(descrs[2], types[1:])

        tariffs_names = [random_word() for _ in range(len(descrs))]
        for i, tariff_name in enumerate(tariffs_names):
            self.cli.add_tariff(tariff_name, descrs[i])
            tariff_detailed_data = self.cli.get_tariff_detailed(tariff_name)
            for service_type_name in tariff_detailed_data['types']:
                rule = 'price = %s' % (Decimal(random.randint(2000, 9000)) / 100)
                self.cli.add_rule(tariff_name, service_type_name, rule)

        self.get_tariff_detailed(tariffs_names, repeats=40)
        self.get_price(self.load_detailed_tariff_data(tariffs_names), repeats=40)
        self.get_wrong_price(self.load_detailed_tariff_data(tariffs_names), repeats=40)

    def test_loading(self):
        self.cli.add_client()
        pool = coros.CoroutinePool(max_size=10)

        waiters = []
        for _ in xrange(1):
            waiters.append(pool.execute_async(self.loader_task))

        for waiter in waiters:
            waiter.wait()


if __name__ == '__main__':
#    cProfile.run('unittest.main()')
    unittest.main()