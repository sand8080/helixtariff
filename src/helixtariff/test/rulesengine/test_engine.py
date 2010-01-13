import unittest
from decimal import Decimal

from helixtariff.test.db_based_test import ServiceTestCase

from helixtariff.rulesengine import engine
from helixtariff.rulesengine.interaction import RequestPrice, PriceProcessingError


class EngineTestCase(ServiceTestCase):
    service_set_name = 'automatic'
    service_types_names = ['registration ru', 'prolongation ru', 'registration com', 'prolongation com']
    tariff_name = 'basic tariff'

    def setUp(self):
        super(EngineTestCase, self).setUp()
        self.add_service_sets([self.service_set_name])
        self.add_types(self.service_types_names)
        self.add_to_service_set(self.service_set_name, self.service_types_names)
        self.add_tariff(self.service_set_name, self.tariff_name, False, None)

    def test_request_price_not_modified(self):
        self.add_rule(self.tariff_name, self.service_types_names[0], '')
        rule = self.get_rule(self.get_root_client().id, self.tariff_name, self.service_types_names[0])
        request = RequestPrice(rule)
        self.assertRaises(PriceProcessingError, engine.process, request)

    def test_request_price(self):
        raw_rule = '''
request.check_period(min_period=1, max_period=3)
price = 15.019

if request.customer_id == 'lucky':
    price = 10.00

if request.period > 1:
    price += 10.00 * (request.period - 1)
'''
        client_id = self.get_root_client().id
        st_name = self.service_types_names[0]
        self.add_rule(self.tariff_name, st_name, raw_rule)
        rule = self.get_rule(client_id, self.tariff_name, st_name)
        response = engine.process(RequestPrice(rule, context={'period': 1}))
        self.assertEqual(Decimal('15.019'), response.price) #IGNORE:W0212
        self.assertEqual('15.019', response.price)

        response = engine.process(RequestPrice(rule, context={'period': 2}))
        self.assertEqual(Decimal('25.019'), response.price) #IGNORE:W0212
        self.assertEqual('25.019', response.price)

        response = engine.process(RequestPrice(rule, context={'period': 3}))
        self.assertEqual(Decimal('35.019'), response.price) #IGNORE:W0212
        self.assertEqual('35.019', response.price)

        response = engine.process(RequestPrice(rule, context={'period': 1, 'customer_id': 'lucky'}))
        self.assertEqual(Decimal('10.00'), response.price) #IGNORE:W0212

        response = engine.process(RequestPrice(rule, context={'period': 2, 'customer_id': 'lucky'}))
        self.assertEqual(Decimal('20.00'), response.price) #IGNORE:W0212

        response = engine.process(RequestPrice(rule, context={'period': 3, 'customer_id': 'lucky'}))
        self.assertEqual(Decimal('30.00'), response.price)  #IGNORE:W0212

        self.assertRaises(PriceProcessingError, engine.process,
            RequestPrice(rule, context={'period': 4}))



if __name__ == '__main__':
    unittest.main()
