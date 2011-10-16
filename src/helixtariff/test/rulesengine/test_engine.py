import unittest

from helixtariff.rulesengine import engine
from helixtariff.rulesengine.engine import RequestPrice
from helixtariff.test.root_test import RootTestCase
from helixtariff.error import RuleCheckingError, RuleProcessingError


class EngineTestCase(RootTestCase):
    def test_request_creation(self):
        req = RequestPrice('')
        self.assertEquals(1, req.objects_num)
        self.assertEquals('', req.rule)

        req = RequestPrice('', objects_num=2, some_param='q')
        self.assertEquals(2, req.objects_num)
        self.assertEquals('q', req.some_param)
        self.assertEquals('', req.rule)

    def test_process(self):
        r = 'price = 15.019'
        req = RequestPrice(r)
        resp = engine.process(req)
        self.assertEquals('15.019', resp.price)

    def test_process_datetime(self):
        r = '''
import datetime

if datetime.datetime.now() >= datetime.datetime(year=2011, month=10, day=16):
    price = 15.50
else:
    price = 10
'''
        req = RequestPrice(r)
        resp = engine.process(req)
        self.assertEquals('15.5', resp.price)

    def test_process_rules_for_number_of_objects(self):
        r = '''
price = 350
if request.objects_num > 1:
    price += 150 * (request.objects_num - 1)
'''
        req = RequestPrice(r)
        resp = engine.process(req)
        self.assertEquals('350', resp.price)

        req = RequestPrice(r, objects_num=2)
        resp = engine.process(req)
        self.assertEquals('500', resp.price)

    def test_process_wrong_rules_failed(self):
        r = 'price = a'
        req = RequestPrice(r)
        self.assertRaises(RuleCheckingError, engine.process, req)

        r = 'price = "a"'
        req = RequestPrice(r)
        self.assertRaises(RuleProcessingError, engine.process, req)

if __name__ == '__main__':
    unittest.main()
