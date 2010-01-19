# coding=utf-8
from eventlet import api, util, coros
from decimal import Decimal
util.wrap_socket_with_coroutine_socket()

import unittest
import datetime
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
        self.cli = Client(settings.server_host, settings.server_port,
            u'егор %s' % datetime.datetime.now(), 'qazwsx')

    def check_status_ok(self, response):
        self.assertEqual('ok', response['status'])

    def load_detailed_tariff_data(self, tariffs_names):
        tariffs = {}
        for n in tariffs_names:
            tariffs[n] = self.cli.get_tariff_detailed(login=self.cli.login, #IGNORE:E1101
                password=self.cli.password, name=n)
        return tariffs

    @profile
    def get_tariff_detailed(self, tariffs_names, repeats=1): #IGNORE:W0613
        tariff_name = select_random(tariffs_names)
        return self.cli.get_tariff_detailed(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
            name=tariff_name)

    @profile
    def view_tariffs(self, repeats=1): #IGNORE:W0613
        return self.cli.view_tariffs(login=self.cli.login, password=self.cli.password) #IGNORE:E1101

    @profile
    def view_detailed_tariffs(self, repeats=1): #IGNORE:W0613
        return self.cli.view_detailed_tariffs(login=self.cli.login, password=self.cli.password) #IGNORE:E1101

    @profile
    def get_price(self, tariffs_detailed, repeats=1): #IGNORE:W0613
        tariff_name = select_random(tariffs_detailed.keys())
        service_types_names = tariffs_detailed[tariff_name]['service_types']
        return self.cli.get_price(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
            tariff=tariff_name, service_type=select_random(service_types_names))

    @profile
    def view_all_prices(self, tariffs_detailed, repeats=1): #IGNORE:W0613
        for n in tariffs_detailed.keys():
            self.cli.view_prices(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
                tariff=n)

    @profile
    def view_prices(self, tariff_name, repeats=1): #IGNORE:W0613
        self.cli.view_prices(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
            tariff=tariff_name)

    @profile
    def get_service_set(self, name, repeats=1): #IGNORE:W0613
        return self.cli.get_service_set(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
            name=name)

    @profile
    def view_service_sets(self, repeats=1): #IGNORE:W0613
        return self.cli.view_service_sets(login=self.cli.login, password=self.cli.password) #IGNORE:E1101

    @profile
    def view_rules(self, tariff_name, repeats=1): #IGNORE:W0613
        return self.cli.view_rules(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
            tariff=tariff_name)

    def loader_task(self):
        types_num = 100
#        types_num = 3
        types = [random_word() for _ in xrange(types_num)]
        print 'Adding types'
        for t in types:
            self.cli.add_service_type(login=self.cli.login, password=self.cli.password, name=t) #IGNORE:E1101
        print 'Types added'

        service_sets_num = 20
#        service_sets_num = 2
        service_sets_names = []
        print 'Adding service sets'
        for _ in xrange(service_sets_num):
            service_set_name = random_word()
            service_sets_names.append(service_set_name)
            types_to_add = types[random.randint(0, types_num / 2):random.randint(types_num / 2 + 1, types_num)]
            self.cli.add_service_set(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
                name=service_set_name, service_types=types_to_add)
            print '.',
        print
        print 'Service sets added'

        self.get_service_set(service_sets_names[0], repeats=1)
        self.get_service_set(service_sets_names[0], repeats=50)
        self.view_service_sets(repeats=1)
        self.view_service_sets(repeats=10)

        tariffs_names = [random_word() for _ in range(service_sets_num)]
        print 'Adding tariffs'
        for i, tariff_name in enumerate(tariffs_names):
            self.cli.add_tariff(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
                name=tariff_name, service_set=service_sets_names[i],
                parent_tariff=None, in_archive=False)
            tariff_detailed_data = self.cli.get_tariff_detailed(login=self.cli.login, #IGNORE:E1101
                password=self.cli.password, name=tariff_name)
            print 'Adding prices for tariff %s' % tariff_name
            for service_type_name in tariff_detailed_data['service_types']:
                print '*',
                rule = 'price = %s' % (Decimal(random.randint(2000, 9000)) / 100)
                self.cli.add_rule(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
                    tariff=tariff_name, service_type=service_type_name, rule=rule)
            print
            print 'Prices added for tariff %s' % tariff_name
        print 'Tariffs added'

        self.view_tariffs(repeats=1)
        self.view_tariffs(repeats=50)
        self.view_detailed_tariffs(repeats=1)
        self.view_detailed_tariffs(repeats=10)
        self.get_tariff_detailed(tariffs_names, repeats=1)
        self.get_tariff_detailed(tariffs_names, repeats=50)
        self.get_price(self.load_detailed_tariff_data(tariffs_names), repeats=1)
        self.get_price(self.load_detailed_tariff_data(tariffs_names), repeats=50)
        self.view_prices(self.load_detailed_tariff_data(tariffs_names).keys()[0], repeats=1)
        self.view_prices(self.load_detailed_tariff_data(tariffs_names).keys()[0], repeats=50)
        self.view_all_prices(self.load_detailed_tariff_data(tariffs_names), repeats=1)
        self.view_rules(tariffs_names[0], repeats=1)
        self.view_rules(tariffs_names[0], repeats=50)

    def test_loading(self):
        self.cli.add_client(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
        pool = coros.CoroutinePool(max_size=10)

        for _ in xrange(1):
            pool.execute_async(self.loader_task)

        pool.wait_all()

    def test_ping_ok(self):
        self.check_status_ok(self.cli.ping()) #IGNORE:E1101

    def test_invalid_request(self):
        response = self.cli.request({'action': 'fakeaction'})
        self.assertEqual('error', response['status'])
        self.assertEqual('validation', response['category'])


if __name__ == '__main__':
    unittest.main()
