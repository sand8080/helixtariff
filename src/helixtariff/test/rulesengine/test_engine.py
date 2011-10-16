from decimal import Decimal
import unittest

from helixtariff.rulesengine import engine
from helixtariff.rulesengine.interaction import RequestPrice, PriceProcessingError
from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase


class EngineTestCase(ActorLogicTestCase):
    def setUp(self):
        super(EngineTestCase, self).setUp()
        self.add_tariff(self.ss_name, self.t_name, False, None)

#    def test_request_price_not_modified(self):
#        st_name = self.st_names[0]
#        self.save_draft_rule(self.t_name, st_name, 'price = 1.0', True)
#        operator = self.get_operator_by_login(self.test_login)
#        tariff = self.get_tariff(operator, self.t_name)
#        service_type = self.get_service_type(operator, st_name)
#        rule = self.get_rule(tariff, service_type, Rule.TYPE_DRAFT)
#        rule.rule = ''
#        request = RequestPrice(rule)
#        self.assertRaises(PriceProcessingError, engine.process, request)

    def test_request_price(self):
        r_text = '''
request.check_period(min_period=1, max_period=3)
price = 15.019

if request.user_id == 34:
    price = 10.00
'''
#        operator = self.get_operator_by_login(self.test_login)
#        st_name = self.st_names[0]
#        self.save_draft_rule(self.t_name, st_name, r_text, True)
#        tariff = self.get_tariff(operator, self.t_name)
#        service_type = self.get_service_type(operator, st_name)
#        rule = self.get_rule(tariff, service_type, Rule.TYPE_DRAFT)
#
#        response = engine.process(RequestPrice(rule, context={'period': 1}))
#        self.assertEqual(Decimal('15.019'), Decimal(response.price))
#
#        response = engine.process(RequestPrice(rule, context={'period': 2}))
#        self.assertEqual(Decimal('25.019'), Decimal(response.price))
#
#        response = engine.process(RequestPrice(rule, context={'period': 3}))
#        self.assertEqual(Decimal('35.019'), Decimal(response.price))
#
#        response = engine.process(RequestPrice(rule, context={'period': 1, 'customer_id': 'lucky'}))
#        self.assertEqual(Decimal('10.00'), Decimal(response.price))
#
#        response = engine.process(RequestPrice(rule, context={'period': 2, 'customer_id': 'lucky'}))
#        self.assertEqual(Decimal('20.00'), Decimal(response.price))
#
#        response = engine.process(RequestPrice(rule, context={'period': 3, 'customer_id': 'lucky'}))
#        self.assertEqual(Decimal('30.00'), Decimal(response.price))
#
#        self.assertRaises(PriceProcessingError, engine.process,
#            RequestPrice(rule, context={'period': 4}))


if __name__ == '__main__':
    unittest.main()
