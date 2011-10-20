import unittest

from helixcore.error import RequestProcessingError

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixtariff.db.dataobject import Rule


class PriceTestCase(ActorLogicTestCase):
#    def test_get_price_no_tariffication_object(self):
#        t_id = self._add_tariff('t')
#        sess = self.login_actor()
#        req = {'session_id': sess.session_id, 'tariff_id': t_id,
#            'tariffication_object_id': 555}
#        self.assertRaises(RequestProcessingError, self.get_price, **req)
#
#    def test_get_price_no_tariff(self):
#        to_id = self._add_tariffication_object('to0')
#        sess = self.login_actor()
#        req = {'session_id': sess.session_id, 'tariff_id': 555,
#            'tariffication_object_id': to_id}
#        self.assertRaises(RequestProcessingError, self.get_price, **req)
#
#    def test_price_not_found(self):
#        t_id = self._add_tariff('t')
#        to_id = self._add_tariffication_object('to0')
#        sess = self.login_actor()
#        req = {'session_id': sess.session_id, 'tariff_id': t_id,
#            'tariffication_object_id': to_id}
#        self.assertRaises(RequestProcessingError, self.get_price, **req)
#
#    def test_price_not_found_with_only_draft_rule(self):
#        t_id = self._add_tariff('t')
#        to_id = self._add_tariffication_object('to0')
#        sess = self.login_actor()
#        req = {'session_id': sess.session_id, 'tariff_id': t_id,
#            'tariffication_object_id': to_id, 'draft_rule': 'price = 10',
#            'status': Rule.STATUS_ACTIVE}
#        resp = self.save_rule(**req)
#        self.check_response_ok(resp)
#        req = {'session_id': sess.session_id, 'tariff_id': t_id,
#            'tariffication_object_id': to_id}
#        self.assertRaises(RequestProcessingError, self.get_price, **req)

    def test_price(self):
        t_name = 't'
        t_id = self._add_tariff(t_name)
        self._add_tariffication_object('to0')
        to_name = 'to1'
        to_id = self._add_tariffication_object(to_name)

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'tariff_id': t_id,
            'tariffication_object_id': to_id, 'draft_rule': 'price = 13.01',
            'status': Rule.STATUS_ACTIVE}
        resp = self.save_rule(**req)
        r_id = resp['id']
        self.check_response_ok(resp)

        req = {'session_id': sess.session_id, 'tariff_id': t_id}
        resp = self.apply_draft_rules(**req)
        self.check_response_ok(resp)

        req = {'session_id': sess.session_id, 'tariff_id': t_id,
            'tariffication_object_id': to_id, 'calculation_context': {}}
        resp = self.get_price(**req)
        self.check_response_ok(resp)
        self.assertEquals(t_id, resp['rule_from_tariff_id'])
        self.assertEquals(t_name, resp['rule_from_tariff_name'])
        self.assertEquals(to_id, resp['tariffication_object_id'])
        self.assertEquals(to_name, resp['tariffication_object_name'])
        self.assertEquals('13.01', resp['price'])
        self.assertEquals(r_id, resp['rule_id'])
        self.assertEquals({}, resp['calculation_context'])


if __name__ == '__main__':
    unittest.main()