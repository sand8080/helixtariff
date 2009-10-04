import unittest
import os

#from helixtariff.rulesengine.rule_checker import RuleChecker
from helixtariff.rulesengine.engine import Engine
from helixtariff.rulesengine.interaction import RequestPrice, PriceProcessingError


class EngineTestCase(unittest.TestCase):
    def read_source(self, file_name):
        file_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), file_name)
        f = open(file_path, 'r')
        return f.read()

    def test_request_price(self):
        e = Engine()
        self.assertRaises(PriceProcessingError, e.process, RequestPrice())


if __name__ == '__main__':
    unittest.main()
