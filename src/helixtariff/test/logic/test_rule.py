import unittest

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixcore.error import RequestProcessingError
from helixtariff.db.dataobject import Rule


class RuleTestCase(ActorLogicTestCase):
    def test_save_rule(self):
        to_id_0 = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t')

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'tariff_id': t_id,
            'tariffication_object_id': to_id_0, 'draft_rule': 'price = 10',
            'status': Rule.STATUS_ACTIVE}
        resp = self.save_rule(**req)
        self.check_response_ok(resp)

        to_id_1 = self._add_tariffication_object('to1')
        req = {'session_id': sess.session_id, 'tariff_id': t_id,
            'tariffication_object_id': to_id_1, 'draft_rule': 'price = 11',
            'status': Rule.STATUS_ACTIVE, 'view_order': 2}
        resp = self.save_rule(**req)
        self.check_response_ok(resp)

    def test_saving_rule_duplicate_failed(self):
        to_id = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t')

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'tariff_id': t_id,
            'tariffication_object_id': to_id, 'status': Rule.STATUS_ACTIVE,
            'draft_rule': 'price = 10'}
        resp = self.save_rule(**req)
        self.check_response_ok(resp)
        self.assertRaises(RequestProcessingError, self.save_rule, **req)

    def test_saving_rule_with_wrong_tariff_failed(self):
        to_id = self._add_tariffication_object('to0')
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'tariff_id': 555,
            'tariffication_object_id': to_id, 'status': Rule.STATUS_ACTIVE,
            'draft_rule': 'price = 10'}
        self.assertRaises(RequestProcessingError, self.save_rule, **req)

    def test_saving_rule_with_wrong_tariffication_object_failed(self):
        t_id = self._add_tariff('t0')
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'tariff_id': t_id,
            'tariffication_object_id': 555, 'status': Rule.STATUS_ACTIVE,
            'draft_rule': 'price = 10'}
        self.assertRaises(RequestProcessingError, self.save_rule, **req)

    def test_saving_rule_with_wrong_id_failed(self):
        to_id = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t0')
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'id': 555,
            'tariff_id': t_id, 'tariffication_object_id': to_id,
            'draft_rule': 'price = 10', 'status': Rule.STATUS_ACTIVE}
        self.assertRaises(RequestProcessingError, self.save_rule, **req)

    def test_saving_wrong_rule_failed(self):
        to_id = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t0')
        sess = self.login_actor()
        req = {'session_id': sess.session_id,
            'tariff_id': t_id, 'tariffication_object_id': to_id,
            'draft_rule': 'price__ = 10', 'status': Rule.STATUS_ACTIVE}
        self.assertRaises(RequestProcessingError, self.save_rule, **req)

    def _get_rules(self, ids):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'filter_params': {'ids': ids},
            'paging_params': {}, 'ordering_params': ['view_order']}
        resp = self.get_rules(**req)
        self.check_response_ok(resp)
        return resp['rules']

    def test_get_rules(self):
        to_name_0 = 'to 0'
        to_id_0 = self._add_tariffication_object(to_name_0)
        to_name_1 = 'to 1'
        to_id_1 = self._add_tariffication_object(to_name_1)
        t_name_0 = 'tariff_0'
        t_id_0 = self._add_tariff(t_name_0)

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'tariff_id': t_id_0,
            'tariffication_object_id': to_id_0, 'draft_rule': 'price = 10',
            'status': Rule.STATUS_ACTIVE, 'view_order': 2}
        resp = self.save_rule(**req)
        self.check_response_ok(resp)
        r_id_0 = resp['id']

        rs_data = self._get_rules([r_id_0])
        r_data = rs_data[0]
        self.assertEquals(1, len(rs_data))
        self.assertEquals(t_id_0, r_data['id'])
        self.assertEquals(to_id_0, r_data['tariffication_object_id'])
        self.assertEquals(to_name_0, r_data['tariffication_object_name'])
        self.assertEquals(t_id_0, r_data['tariff_id'])
        self.assertEquals(t_name_0, r_data['tariff_name'])
        self.assertEquals(2, r_data['view_order'])
        self.assertEquals(None, r_data['rule'])
        self.assertNotEquals(None, r_data['draft_rule'])

        # checking sorting by view_order
        req = {'session_id': sess.session_id, 'tariff_id': t_id_0,
            'tariffication_object_id': to_id_1, 'draft_rule': 'price = 11',
            'status': Rule.STATUS_ACTIVE, 'view_order': 1}
        resp = self.save_rule(**req)
        self.check_response_ok(resp)
        r_id_1 = resp['id']

        req = {'session_id': sess.session_id, 'filter_params': {'ids': [r_id_0, r_id_1]},
            'paging_params': {}, 'ordering_params': ['view_order']}
        resp = self.get_rules(**req)
        self.check_response_ok(resp)
        self.assertEquals(2, resp['total'])
        self.assertEquals(r_id_1, resp['rules'][0]['id'])
        self.assertEquals(r_id_0, resp['rules'][1]['id'])

    def test_delete_rule(self):
        t_id = self._add_tariff('t')
        to_id = self._add_tariffication_object('to')

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'tariff_id': t_id,
            'tariffication_object_id': to_id, 'draft_rule': 'price = 10',
            'status': Rule.STATUS_ACTIVE}
        resp = self.save_rule(**req)
        self.check_response_ok(resp)
        r_id = resp['id']

        req = {'session_id': sess.session_id, 'id': t_id}
        resp = self.delete_rule(**req)
        self.check_response_ok(resp)
        rs_data = self._get_rules([r_id])
        self.assertEquals(0, len(rs_data))

    def test_apply_draft_rules(self):
        t_id = self._add_tariff('t')
        to_id = self._add_tariffication_object('to')

        sess = self.login_actor()
        r = 'price = 10'
        req = {'session_id': sess.session_id, 'tariff_id': t_id,
            'tariffication_object_id': to_id, 'draft_rule': r,
            'status': Rule.STATUS_ACTIVE}
        resp = self.save_rule(**req)
        self.check_response_ok(resp)
        r_id = resp['id']

        req = {'session_id': sess.session_id, 'tariff_id': t_id}
        resp = self.apply_draft_rules(**req)
        self.check_response_ok(resp)

        rs_data = self._get_rules([r_id])
        self.assertEquals(1, len(rs_data))
        r_data = rs_data[0]
        self.assertEquals(r, r_data['rule'])
        self.assertEquals(None, r_data['draft_rule'])

    def test_apply_draft_rules_with_empty_draft_rule(self):
        t_id = self._add_tariff('t')
        to_id = self._add_tariffication_object('to')

        sess = self.login_actor()
        r = 'price = 10'
        req = {'session_id': sess.session_id, 'tariff_id': t_id,
            'tariffication_object_id': to_id, 'draft_rule': r,
            'status': Rule.STATUS_ACTIVE}
        resp = self.save_rule(**req)
        self.check_response_ok(resp)
        r_id = resp['id']

        req = {'session_id': sess.session_id, 'tariff_id': t_id}
        resp = self.apply_draft_rules(**req)
        self.check_response_ok(resp)
        req = {'session_id': sess.session_id, 'tariff_id': t_id}
        resp = self.apply_draft_rules(**req)
        self.check_response_ok(resp)

        rs_data = self._get_rules([r_id])
        self.assertEquals(1, len(rs_data))
        r_data = rs_data[0]
        self.assertEquals(r, r_data['rule'])
        self.assertEquals(None, r_data['draft_rule'])

    def test_apply_draft_rules_with_wrong_tariff(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'tariff_id': 777}
        self.assertRaises(RequestProcessingError, self.apply_draft_rules, **req)


if __name__ == '__main__':
    unittest.main()