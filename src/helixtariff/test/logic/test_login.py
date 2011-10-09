import unittest

from helixcore.test.logic import access_granted #@UnusedImport
from helixtariff.test.logic.logic_test import LogicTestCase


class LoginTestCase(LogicTestCase):
    def test_login(self):
        req = {'environment_name': 'n', 'login': 'l', 'password': 'p'}
        resp = self.login(**req)
        self.check_response_ok(resp)
        self.assertEquals(access_granted.GRANTED_SESSION_ID, resp['session_id'])
        self.assertEquals(access_granted.GRANTED_USER_ID, resp['user_id'])
        self.assertEquals(access_granted.GRANTED_ENV_ID, resp['environment_id'])


if __name__ == '__main__':
    unittest.main()