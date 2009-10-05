import unittest
from decimal import Decimal

from helixtariff.test.db_based_test import ServiceTestCase

from helixtariff.rulesengine.engine import Engine
from helixtariff.rulesengine.checker import RuleError
from helixtariff.rulesengine.interaction import RequestDomainPrice, PriceProcessingError


class EngineTestCase(ServiceTestCase):
    service_set_descr_name = 'automatic'
    service_types_names = ['registration ru', 'prolongation ru', 'registration com', 'prolongation com']
    tariff_name = 'basic tariff'

    def setUp(self):
        super(EngineTestCase, self).setUp()
        self.add_descrs([self.service_set_descr_name])
        self.add_types(self.service_types_names)
        self.add_to_service_set(self.service_set_descr_name, self.service_types_names)
        self.add_tariff(self.service_set_descr_name, self.tariff_name, False)

    def test_request_price_not_modified(self):
        self.add_rule(self.tariff_name, self.service_types_names[0], '')
        e = Engine()
        request = RequestDomainPrice(self.get_root_client().id, self.tariff_name, self.service_types_names[0])
        self.assertRaises(PriceProcessingError, e.process, request)

    def test_request_price(self):
        rule = '''
request.check_period(min_period=1, max_period=3)
price = 15.01

if request.customer_id == 'lucky':
    price = 10.00

if request.period > 1:
    price += 10.00 * (request.period - 1)
'''
        self.add_rule(self.tariff_name, self.service_types_names[0], rule)

        e = Engine()
        cleint_id = self.get_root_client().id
        response = e.process(RequestDomainPrice(cleint_id, self.tariff_name,
            self.service_types_names[0]))
        self.assertEqual(Decimal('15.01'), response.price)

        response = e.process(RequestDomainPrice(cleint_id, self.tariff_name,
            self.service_types_names[0], period=2))
        self.assertEqual(Decimal('25.01'), response.price)

        response = e.process(RequestDomainPrice(cleint_id, self.tariff_name,
            self.service_types_names[0], period=3))
        self.assertEqual(Decimal('35.01'), response.price)

        response = e.process(RequestDomainPrice(cleint_id, self.tariff_name,
            self.service_types_names[0], customer_id='lucky'))
        self.assertEqual(Decimal('10.00'), response.price)

        response = e.process(RequestDomainPrice(cleint_id, self.tariff_name,
            self.service_types_names[0], period=2, customer_id='lucky'))
        self.assertEqual(Decimal('20.00'), response.price)

        response = e.process(RequestDomainPrice(cleint_id, self.tariff_name,
            self.service_types_names[0], period=3, customer_id='lucky'))
        self.assertEqual(Decimal('30.00'), response.price)

        self.assertRaises(PriceProcessingError, e.process,
            RequestDomainPrice(cleint_id, self.tariff_name, self.service_types_names[0], period=4))


if __name__ == '__main__':
    unittest.main()
