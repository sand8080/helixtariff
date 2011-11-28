import unittest

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase


class CurrencyTestCase(ActorLogicTestCase):
    def test_get_currencies(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id}
        resp = self.get_currencies(**req)
        self.check_response_ok(resp)


if __name__ == '__main__':
    unittest.main()
