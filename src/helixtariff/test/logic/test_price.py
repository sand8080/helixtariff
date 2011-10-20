import unittest

from helixcore.error import RequestProcessingError

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixtariff.db.dataobject import Rule, Tariff


class PriceTestCase(ActorLogicTestCase):
    def test_get_price_no_tariffication_object(self):
        t_id = self._add_tariff('t')
        self.assertRaises(RequestProcessingError, self._get_price, t_id, 555)

    def test_get_price_no_tariff(self):
        to_id = self._add_tariffication_object('to0')
        self.assertRaises(RequestProcessingError, self._get_price, 555, to_id)

    def test_price_not_found(self):
        t_id = self._add_tariff('t')
        to_id = self._add_tariffication_object('to0')
        self.assertRaises(RequestProcessingError, self._get_price, t_id, to_id)

    def test_price_not_found_with_only_draft_rule(self):
        t_id = self._add_tariff('t')
        to_id = self._add_tariffication_object('to0')
        self._save_rule(t_id, to_id, 'price = 10')
        self.assertRaises(RequestProcessingError, self._get_price, t_id, to_id)

    def test_price(self):
        t_name = 't'
        t_id = self._add_tariff(t_name)
        self._add_tariffication_object('to0')
        to_name = 'to1'
        to_id = self._add_tariffication_object(to_name)
        r_id = self._save_rule(t_id, to_id, 'price = 13.01')
        self._apply_draft_rules(t_id)

        resp = self._get_price(t_id, to_id, calculation_ctx={})
        self.assertEquals(t_id, resp['rule_from_tariff_id'])
        self.assertEquals(t_name, resp['rule_from_tariff_name'])
        self.assertEquals(to_id, resp['tariffication_object_id'])
        self.assertEquals(to_name, resp['tariffication_object_name'])
        self.assertEquals('13.01', resp['price'])
        self.assertEquals(r_id, resp['rule_id'])
        self.assertEquals({}, resp['calculation_context'])

    def test_price_inheritance(self):
        # Adding tariffs
        p_t_name = 'p_t'
        p_t_id = self._add_tariff(p_t_name)
        ch_t_name = 'ch_t'
        ch_t_id = self._add_tariff(ch_t_name, parent_tariff_id=p_t_id)

        # Adding tariffication object
        self._add_tariffication_object('to0')
        to_name = 'to1'
        to_id = self._add_tariffication_object(to_name)

        # Saving rule to parent tariff
        p_r_id = self._save_rule(p_t_id, to_id, 'price = 13.02')

        # Rule not applied yet
        self.assertRaises(RequestProcessingError, self._get_price, ch_t_id, to_id)

        # Applying rules
        self._apply_draft_rules(p_t_id)

        # Now rule already applied. Getting price for child tariff
        resp = self._get_price(ch_t_id, to_id)
        self.assertEquals(p_t_id, resp['rule_from_tariff_id'])
        self.assertEquals(p_t_name, resp['rule_from_tariff_name'])
        self.assertEquals(to_id, resp['tariffication_object_id'])
        self.assertEquals(to_name, resp['tariffication_object_name'])
        self.assertEquals('13.02', resp['price'])
        self.assertEquals(p_r_id, resp['rule_id'])

        # Checking rule overloading in child tariff
        ch_r_id = self._save_rule(ch_t_id, to_id, 'price = 12.01')
        self._apply_draft_rules(ch_t_id)

        # Checking rule overloaded
        resp = self._get_price(ch_t_id, to_id)
        self.assertEquals(ch_t_id, resp['rule_from_tariff_id'])
        self.assertEquals(ch_t_name, resp['rule_from_tariff_name'])
        self.assertEquals(to_id, resp['tariffication_object_id'])
        self.assertEquals(to_name, resp['tariffication_object_name'])
        self.assertEquals('12.01', resp['price'])
        self.assertEquals(ch_r_id, resp['rule_id'])

    def test_tariff_inactivated(self):
        t_name = 'p_t'
        p_t_id = self._add_tariff(t_name, status=Tariff.STATUS_INACTIVE)
        ch_t_name = 'ch_t'
        ch_t_id = self._add_tariff(ch_t_name, parent_tariff_id=p_t_id)
        self._add_tariffication_object('to0')
        to_name = 'to1'
        to_id = self._add_tariffication_object(to_name)
        self._save_rule(p_t_id, to_id, 'price = 1')
        self._apply_draft_rules(p_t_id)

        self.assertRaises(RequestProcessingError, self._get_price, p_t_id, to_id)
        self.assertRaises(RequestProcessingError, self._get_price, ch_t_id, to_id)

        # Adding rule to active child tariff
        self._save_rule(ch_t_id, to_id, 'price = 2')
        self._apply_draft_rules(ch_t_id)
        resp = self._get_price(ch_t_id, to_id)
        self.assertEquals('2', resp['price'])

    def test_rule_inactivated(self):
        t_name = 'p_t'
        t_id = self._add_tariff(t_name)
        to_id = self._add_tariffication_object('to')
        r_id = self._save_rule(t_id, to_id, 'price = 1')
        self._apply_draft_rules(t_id)

        # Checking price calculation
        resp = self._get_price(t_id, to_id)
        self.assertEquals('1', resp['price'])

        # Rule inactivation
        self._save_rule(t_id, to_id, 'price = 2',
            status=Rule.STATUS_INACTIVE, id=r_id)

        # Checking price not found
        self.assertRaises(RequestProcessingError, self._get_price, t_id, to_id)

    def test_inactive_tariff_in_chain(self):
        to_id = self._add_tariffication_object('to')
        t_id_0 = self._add_tariff('t0')
        t_id_1 = self._add_tariff('t1', parent_tariff_id=t_id_0)
        t_id_2 = self._add_tariff('t2', parent_tariff_id=t_id_1)

        self._save_rule(t_id_0, to_id, 'price = 1')
        self._apply_draft_rules(t_id_0)
        self._save_rule(t_id_1, to_id, 'price = 2')
        self._apply_draft_rules(t_id_1)

        # Checking price calculation
        resp = self._get_price(t_id_2, to_id)
        self.assertEquals('2', resp['price'])

        # Tariff inactivation
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'id': t_id_1,
            'new_status': Tariff.STATUS_INACTIVE}
        resp = self.modify_tariff(**req)
        self.check_response_ok(resp)

        # Checking price calculated from parent tariff 0
        resp = self._get_price(t_id_2, to_id)
        self.assertEquals('1', resp['price'])


if __name__ == '__main__':
    unittest.main()