import unittest

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixcore.error import RequestProcessingError
from helixtariff.db.dataobject import Rule


class RuleTestCase(ActorLogicTestCase):
    def test_save_rule(self):
        to_id_0 = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t')

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'rules': [{
            'tariff_id': t_id, 'tariffication_object_id': to_id_0,
            'draft_rule': 'price = 10', 'status': Rule.STATUS_ACTIVE}]}
        resp = self.save_rules(**req)
        self.check_response_ok(resp)
        r_id_0 = resp['ids'][0]

        to_id_1 = self._add_tariffication_object('to1')
        req = {'session_id': sess.session_id, 'rules': [
            {
                'id': r_id_0, 'tariff_id': t_id, 'status': Rule.STATUS_ACTIVE,
                'tariffication_object_id': to_id_0, 'draft_rule': 'price = 11'
            },
            {
                'tariff_id': t_id, 'status': Rule.STATUS_ACTIVE,
                'tariffication_object_id': to_id_1, 'draft_rule': 'price = 12'
            },
        ]}
        resp = self.save_rules(**req)
        self.check_response_ok(resp)
        r_id_0 = resp['ids'][0]
        # TODO: add checking by get operation

    def test_saving_rule_duplicate_failed(self):
        to_id = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t')

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'rules': [{
            'tariff_id': t_id, 'tariffication_object_id': to_id,
            'draft_rule': 'price = 10', 'status': Rule.STATUS_ACTIVE}]}
        resp = self.save_rules(**req)
        self.check_response_ok(resp)

        self.assertRaises(RequestProcessingError, self.save_rules, **req)

    def test_saving_rule_with_wrong_tariff_failed(self):
        to_id = self._add_tariffication_object('to0')
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'rules': [{
            'tariff_id': 555, 'tariffication_object_id': to_id,
            'draft_rule': 'price = 10', 'status': Rule.STATUS_ACTIVE}]}
        self.assertRaises(RequestProcessingError, self.save_rules, **req)

    def test_saving_rule_with_wrong_tariffication_object_failed(self):
        t_id = self._add_tariff('t0')
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'rules': [{
            'tariff_id': t_id, 'tariffication_object_id': 555,
            'draft_rule': 'price = 10', 'status': Rule.STATUS_ACTIVE}]}
        self.assertRaises(RequestProcessingError, self.save_rules, **req)

    def test_saving_rule_with_wrong_id(self):
        to_id = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t0')
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'rules': [{'id': 555,
            'tariff_id': t_id, 'tariffication_object_id': to_id,
            'draft_rule': 'price = 10', 'status': Rule.STATUS_ACTIVE}]}
        self.assertRaises(RequestProcessingError, self.save_rules, **req)


if __name__ == '__main__':
    unittest.main()