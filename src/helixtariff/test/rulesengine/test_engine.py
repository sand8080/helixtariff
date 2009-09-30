import unittest
import os

#from helixtariff.rulesengine.rule_checker import RuleChecker
from helixtariff.rulesengine.engine import Engine, EngineError
from helixtariff.rulesengine.interaction import RequestPrice


class EngineTestCase(unittest.TestCase):
    def read_source(self, file_name):
        file_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), file_name)
        f = open(file_path, 'r')
        return f.read()

    def test_request_price(self):
        e = Engine()
        request = RequestPrice()
        e.process(request)
        self.assertRaises(EngineError, e.process, '')


if __name__ == '__main__':
    unittest.main()
