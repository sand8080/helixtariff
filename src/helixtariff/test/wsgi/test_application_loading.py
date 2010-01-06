from eventlet import api, util, coros
from decimal import Decimal
util.wrap_socket_with_coroutine_socket()

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
    def view_tariffs(self, repeats=1): #IGNORE:W0613
        return self.cli.view_tariffs()

    @profile
    def view_detailed_tariffs(self, repeats=1): #IGNORE:W0613
        return self.cli.view_detailed_tariffs()

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

    @profile
    def view_service_set(self, name, repeats=1): #IGNORE:W0613
        return self.cli.view_service_set(name)

    @profile
    def view_service_sets(self, repeats=1): #IGNORE:W0613
        return self.cli.view_service_sets()

    def loader_task(self):
        types_num = 100
        types = [random_word() for _ in xrange(types_num)]
        print 'Adding types'
        map(self.cli.add_service_type, types)
        print 'Types added'

        service_sets_num = 20
        service_sets_names = []
        print 'Adding service sets'
        for _ in xrange(service_sets_num):
            service_set_name = random_word()
            service_sets_names.append(service_set_name)
            self.cli.add_service_set(service_set_name)
            types_to_add = types[random.randint(0, types_num / 2):random.randint(types_num / 2 + 1, types_num)]
            self.cli.add_to_service_set(service_set_name, types_to_add)
            print '.',
        print
        print 'Service sets added'

        self.view_service_set(service_sets_names[0], repeats=50)
        self.view_service_sets(repeats=5)

        tariffs_names = [random_word() for _ in range(service_sets_num)]
        print 'Adding tariffs'
        for i, tariff_name in enumerate(tariffs_names):
            self.cli.add_tariff(tariff_name, service_sets_names[i])
            tariff_detailed_data = self.cli.get_tariff_detailed(tariff_name)
            print 'Adding prices for tariff %s' % tariff_name
            for service_type_name in tariff_detailed_data['types']:
                print '*',
                rule = 'price = %s' % (Decimal(random.randint(2000, 9000)) / 100)
                self.cli.add_rule(tariff_name, service_type_name, rule)
            print
            print 'Prices added for tariff %s' % tariff_name
        print 'Tariffs added'

        self.view_tariffs(repeats=50)
        self.view_detailed_tariffs(repeats=10)
        self.get_tariff_detailed(tariffs_names, repeats=50)
        self.get_price(self.load_detailed_tariff_data(tariffs_names), repeats=50)
        self.get_wrong_price(self.load_detailed_tariff_data(tariffs_names), repeats=50)

    def test_loading(self):
        self.cli.add_client()
        pool = coros.CoroutinePool(max_size=10)

        for _ in xrange(1):
            pool.execute_async(self.loader_task)

        pool.wait_all()

    def test_ping_ok(self):
        self.check_status_ok(self.cli.ping())

    def test_invalid_request(self):
        raw_result = self.cli.request({'action': 'fakeaction'})
        result = cjson.decode(raw_result)
        self.assertEqual('error', result['status'])
        self.assertEqual('validation', result['category'])


if __name__ == '__main__':
    unittest.main()
