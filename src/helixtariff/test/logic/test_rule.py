import unittest

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixcore.error import RequestProcessingError


class RuleTestCase(ActorLogicTestCase):
    def test_save_rule(self):
        to_id_0 = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t')
        self._save_rule(t_id, to_id_0, 'price = 10')

        to_id_1 = self._add_tariffication_object('to1')
        r_id_1 = self._save_rule(t_id, to_id_1, 'price = 10')
        self._save_rule(t_id, to_id_1, 'price = 10', id=r_id_1)

    def test_saving_rule_duplicate_failed(self):
        to_id = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t')
        self._save_rule(t_id, to_id, 'price = 1')
        self.assertRaises(RequestProcessingError, self._save_rule, t_id, to_id, 'price = 1')

    def test_saving_rule_with_wrong_tariff_failed(self):
        to_id = self._add_tariffication_object('to0')
        self.assertRaises(RequestProcessingError, self._save_rule, 555, to_id, 'price = 2')

    def test_saving_rule_with_wrong_tariffication_object_failed(self):
        t_id = self._add_tariff('t0')
        self.assertRaises(RequestProcessingError, self._save_rule, t_id, 555, 'price = 3')

    def test_saving_rule_with_wrong_id_failed(self):
        to_id = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t0')
        self.assertRaises(RequestProcessingError, self._save_rule, t_id, to_id,
            {'id': 555})

    def test_saving_wrong_rule_failed(self):
        to_id = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t0')
        self.assertRaises(RequestProcessingError, self._save_rule, t_id, to_id,
            'price_fail = 10')

    def test_get_rules(self):
        to_name_0 = 'to 0'
        to_id_0 = self._add_tariffication_object(to_name_0)
        to_name_1 = 'to 1'
        to_id_1 = self._add_tariffication_object(to_name_1)
        t_name_0 = 'tariff_0'
        t_id_0 = self._add_tariff(t_name_0)
        r_id_0 = self._save_rule(t_id_0, to_id_0, 'price = 10', view_order=2)

        sess = self.login_actor()
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
        r_id_1 = self._save_rule(t_id_0, to_id_1, 'price = 11',
            view_order=1)

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
        r_id = self._save_rule(t_id, to_id, 'price = 10')

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'id': t_id}
        resp = self.delete_rule(**req)
        self.check_response_ok(resp)
        rs_data = self._get_rules([r_id])
        self.assertEquals(0, len(rs_data))

    def test_apply_draft_rules(self):
        t_id = self._add_tariff('t')
        to_id = self._add_tariffication_object('to')

        r = 'price = 10'
        r_id = self._save_rule(t_id, to_id, r)
        self._apply_draft_rules(t_id)

        rs_data = self._get_rules([r_id])
        self.assertEquals(1, len(rs_data))
        r_data = rs_data[0]
        self.assertEquals(r, r_data['rule'])
        self.assertEquals(None, r_data['draft_rule'])

    def test_apply_draft_rules_with_empty_draft_rule(self):
        t_id = self._add_tariff('t')
        to_id = self._add_tariffication_object('to')

        r = 'price = 10'
        r_id = self._save_rule(t_id, to_id, r)
        self._apply_draft_rules(t_id)
        self._apply_draft_rules(t_id)

        rs_data = self._get_rules([r_id])
        self.assertEquals(1, len(rs_data))
        r_data = rs_data[0]
        self.assertEquals(r, r_data['rule'])
        self.assertEquals(None, r_data['draft_rule'])

    def test_apply_draft_rules_with_wrong_tariff(self):
        self.assertRaises(RequestProcessingError, self._apply_draft_rules, 555)


if __name__ == '__main__':
    unittest.main()