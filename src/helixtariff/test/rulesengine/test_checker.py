import unittest

from helixtariff.rulesengine.checker import RuleChecker, RuleError

class RuleCheckerTestCase(unittest.TestCase):
    checker = RuleChecker()

    def test_denied_names(self):
        self.assertRaises(RuleError, self.checker.check, 'import os')
        self.assertRaises(RuleError, self.checker.check, 'os.path')
        self.assertRaises(RuleError, self.checker.check, 'exec')
        self.assertRaises(RuleError, self.checker.check, 'print')
        self.assertRaises(RuleError, self.checker.check, '''open('/etc/passwd')''')

    def test_correct_rule(self):
        self.checker.check('if context.get_balance(request.customer_id) > 300: response.price += 50')


if __name__ == '__main__':
    unittest.main()