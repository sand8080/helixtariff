import unittest

from helixtariff.rulesengine.engine import Engine
from helixtariff.server.request import PriceCalculationRequest

class EngineTestCase(unittest.TestCase):
    eng = Engine()

    def test_process_unknown_request_type(self):
        self.assertRaises(NotImplementedError, self.eng.process, '')

    def test_process(self):
        self.eng.process(PriceCalculationRequest('cli 1', 'noname', 'register ru', 'cust 7'))


if __name__ == '__main__':
    unittest.main()
