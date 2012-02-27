import unittest

from helixcore.error import RequestProcessingError

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase


class UserTariffTestCase(ActorLogicTestCase):
    u_id = 22

    def test_add_user_tariff(self):
        t_id = self._add_tariff('tariff one', currency='RUB')
        self._add_user_tariff(t_id, self.u_id)

    def test_add_user_tariff_duplication(self):
        name = 'tariff one'
        t_id = self._add_tariff(name, currency='RUB')
        self._add_user_tariff(t_id, self.u_id)
        self.assertRaises(RequestProcessingError, self._add_user_tariff, t_id, self.u_id)

    def test_add_wrong_tariff(self):
        self.assertRaises(RequestProcessingError, self._add_user_tariff, 555, self.u_id)

    def test_delete_user_tariff(self):
        t_id = self._add_tariff('t', currency='RUB')
        self._add_user_tariff(t_id, self.u_id)

        user_tariffs = self._get_user_tariffs([self.u_id])
        self.assertEquals([t_id], user_tariffs[0]['tariff_ids'])

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'user_id': self.u_id,
            'tariff_ids': [t_id]}
        resp = self.delete_user_tariffs(**req)
        self.check_response_ok(resp)

        user_tariffs = self._get_user_tariffs([self.u_id])
        self.assertEquals(0, len(user_tariffs))

    def test_get_user_tariffs(self):
        self._add_tariff('t0', currency='RUB')
        t_id_1 = self._add_tariff('t1', currency='RUB')

        user_tariffs = self._get_user_tariffs([self.u_id])
        self.assertEquals(0, len(user_tariffs))

        self._add_user_tariff(t_id_1, self.u_id)
        user_tariffs = self._get_user_tariffs([self.u_id])
        self.assertEquals(1, len(user_tariffs))
        self.assertEquals(self.u_id, user_tariffs[0]['user_id'])
        self.assertEquals([t_id_1], user_tariffs[0]['tariff_ids'])


if __name__ == '__main__':
    unittest.main()