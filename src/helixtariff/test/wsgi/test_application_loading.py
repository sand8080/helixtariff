from eventlet import api, util, coros
util.wrap_socket_with_coroutine_socket()

from decimal import Decimal
import unittest
import datetime
import cjson
import random

from helixcore.test.util import random_word, select_random, profile

from helixtariff.test.db_based_test import DbBasedTestCase
from helixtariff.conf import settings
from helixtariff.test.wsgi.client import Client
from helixtariff.wsgi.server import Server


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

        service_sets = [random_word() for _ in range(3)]
        map(self.cli.add_service_set, service_sets)

        self.cli.add_to_service_set(service_sets[0], types)
        self.cli.add_to_service_set(service_sets[1], types[:2])
        self.cli.add_to_service_set(service_sets[2], types[1:])

        tariffs_names = [random_word() for _ in range(len(service_sets))]
        for i, tariff_name in enumerate(tariffs_names):
            self.cli.add_tariff(tariff_name, service_sets[i])
            tariff_detailed_data = self.cli.get_tariff_detailed(tariff_name)
            for service_type_name in tariff_detailed_data['types']:
                rule = 'price = %s' % (Decimal(random.randint(2000, 9000)) / 100)
                self.cli.add_rule(tariff_name, service_type_name, rule)

        self.get_tariff_detailed(tariffs_names, repeats=50)
        self.get_price(self.load_detailed_tariff_data(tariffs_names), repeats=50)
        self.get_wrong_price(self.load_detailed_tariff_data(tariffs_names), repeats=50)

    def test_loading(self):
        self.cli.add_client()
        pool = coros.CoroutinePool(max_size=10)

        for _ in xrange(1):
            pool.execute_async(self.loader_task)

        pool.wait_all()

if __name__ == '__main__':
    unittest.main()
