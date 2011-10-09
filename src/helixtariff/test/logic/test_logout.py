import unittest

from helixtariff.test.logic.logic_test import LogicTestCase


class LogoutTestCase(LogicTestCase):
    def test_logout(self):
        from helixcore.test.logic import access_granted #@UnusedImport
        req = {'session_id': 's'}
        resp = self.logout(**req)
        self.check_response_ok(resp)


if __name__ == '__main__':
    unittest.main()