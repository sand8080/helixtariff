import unittest

from helixtariff.rulesengine.checker import RuleChecker
from helixtariff.error import RuleCheckingError


class RuleCheckerTestCase(unittest.TestCase):
    checker = RuleChecker()

    def test_denied_names(self):
        self.assertRaises(RuleCheckingError, self.checker.check, 'import os')
        self.assertRaises(RuleCheckingError, self.checker.check, 'os.path')
        self.assertRaises(RuleCheckingError, self.checker.check, 'exec')
        self.assertRaises(RuleCheckingError, self.checker.check, 'print')
        self.assertRaises(RuleCheckingError, self.checker.check, '''open('/etc/passwd')''')

    def test_rule(self):
        self.checker.check('price = 50')
        self.checker.check('''
price = 50
if request.objects_num > 1:
    price += 35 * (request.objects_num - 1)
''')


if __name__ == '__main__':
    unittest.main()