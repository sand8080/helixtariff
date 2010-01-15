# coding=utf-8
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
        self.cli = Client(settings.server_host, settings.server_port,
            u'егор %s' % datetime.datetime.now(), 'qazwsx')

    def check_status_ok(self, raw_result):
        self.assertEqual('ok', cjson.decode(raw_result)['status'])

    def load_detailed_tariff_data(self, tariffs_names):
        tariffs = {}
        for n in tariffs_names:
            tariffs[n] = self.cli.get_tariff_detailed(n) #IGNORE:E1101
        return tariffs

    @profile
    def get_tariff_detailed(self, tariffs_names, repeats=1): #IGNORE:W0613
        tariff_name = select_random(tariffs_names)
        return self.cli.get_tariff_detailed(tariff_name) #IGNORE:E1101

    @profile
    def view_tariffs(self, repeats=1): #IGNORE:W0613
        return self.cli.view_tariffs() #IGNORE:E1101

    @profile
    def view_detailed_tariffs(self, repeats=1): #IGNORE:W0613
        return self.cli.view_detailed_tariffs() #IGNORE:E1101

    @profile
    def get_price(self, tariffs_detailed, repeats=1): #IGNORE:W0613
        tariff_name = select_random(tariffs_detailed.keys())
        service_types_names = tariffs_detailed[tariff_name]['types']
        return self.cli.get_price(tariff_name, select_random(service_types_names)) #IGNORE:E1101

    @profile
    def view_prices(self, tariffs_detailed, repeats=1): #IGNORE:W0613
        tariff_name = select_random(tariffs_detailed.keys())
        return self.cli.view_prices(tariff_name)  #IGNORE:E1101

    @profile
    def get_wrong_price(self, tariffs_detailed, repeats=1): #IGNORE:W0613
        tariff_name = select_random(tariffs_detailed.keys())
        service_types_names = tariffs_detailed[tariff_name]['types']
        return self.cli.get_price(tariff_name, select_random(service_types_names) + 'fake')  #IGNORE:E1101

    @profile
    def get_service_set(self, name, repeats=1): #IGNORE:W0613
        return self.cli.get_service_set(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
            name=name)

    @profile
    def view_service_sets(self, repeats=1): #IGNORE:W0613
        return self.cli.view_service_sets(login=self.cli.login, password=self.cli.password) #IGNORE:E1101

    @profile
    def view_rules(self, tariff_name, repeats=1): #IGNORE:W0613
        return self.cli.view_rules(tariff_name) #IGNORE:E1101

    def loader_task(self):
        types_num = 100
        types = [random_word() for _ in xrange(types_num)]
        print 'Adding types'
        for t in types:
            self.cli.add_service_type(login=self.cli.login, password=self.cli.password, name=t) #IGNORE:E1101
        print 'Types added'

        service_sets_num = 20
        service_sets_names = []
        print 'Adding service sets'
        for _ in xrange(service_sets_num):
            service_set_name = random_word()
            service_sets_names.append(service_set_name)
            self.cli.add_service_set(login=self.cli.login, password=self.cli.password, name=service_set_name)#IGNORE:E1101
            types_to_add = types[random.randint(0, types_num / 2):random.randint(types_num / 2 + 1, types_num)]
            self.cli.add_to_service_set(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
                name=service_set_name, types=types_to_add)
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
            for service_type_name in tariff_detailed_data['types']:
                print '*',
                rule = 'price = %s' % (Decimal(random.randint(2000, 9000)) / 100)
                self.cli.add_rule(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
                    tariff=tariff_name, service_type=service_type_name, rule=rule)
            print
            print 'Prices added for tariff %s' % tariff_name
        print 'Tariffs added'
#        self.view_tariffs(repeats=1)
#        self.view_tariffs(repeats=50)
#        self.view_detailed_tariffs(repeats=1)
#        self.view_detailed_tariffs(repeats=10)
#        self.get_tariff_detailed(tariffs_names, repeats=1)
#        self.get_tariff_detailed(tariffs_names, repeats=50)
#        self.get_price(self.load_detailed_tariff_data(tariffs_names), repeats=1)
#        self.get_price(self.load_detailed_tariff_data(tariffs_names), repeats=50)
#        self.view_prices(self.load_detailed_tariff_data(tariffs_names), repeats=1)
#        self.view_prices(self.load_detailed_tariff_data(tariffs_names), repeats=50)
#        self.get_wrong_price(self.load_detailed_tariff_data(tariffs_names), repeats=1)
#        self.get_wrong_price(self.load_detailed_tariff_data(tariffs_names), repeats=50)
#        self.view_rules(tariffs_names[0], repeats=1)
#        self.view_rules(tariffs_names[0], repeats=50)

    def test_loading(self):
        self.cli.add_client(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
        pool = coros.CoroutinePool(max_size=10)

        for _ in xrange(1):
            pool.execute_async(self.loader_task)

        pool.wait_all()

#    def test_ping_ok(self):
#        self.check_status_ok(self.cli.ping()) #IGNORE:E1101
#    def test_invalid_request(self):
#        raw_result = self.cli.request({'action': 'fakeaction'})
#        result = cjson.decode(raw_result)
#        self.assertEqual('error', result['status'])
#        self.assertEqual('validation', result['category'])


if __name__ == '__main__':
    unittest.main()
