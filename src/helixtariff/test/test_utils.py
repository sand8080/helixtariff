import unittest

from helixtariff import utils


class UtilsTestCase(unittest.TestCase):
    def test_format_price(self):
        values = ['5.01', '11.1', '11.12', '10.00', '509']
        expected = ['5.01', '11.1', '11.12', '10', '509']
        actual = []
        for v in values:
            actual.append(utils.format_price(v))
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
