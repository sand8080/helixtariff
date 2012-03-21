import unittest

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixtariff.db.dataobject import Tariff
from helixcore.error import RequestProcessingError


class TariffViewingContextCase(ActorLogicTestCase):
    def test_add_tariff_viewing_context(self):
        t_id = self._add_tariff('t', currency='RUB')
        t_v_name = 'first'
        context = [{'name': 'num', 'value': 4}, {'name': 'param', 'value': 'like'}]
        view_order = 1
        t_v_id = self._add_tariff_viewing_context(t_v_name,
            t_id, context, view_order=view_order)
        t_v_ctxs = self._tariff_viewing_contexts_data(t_id)
        self.assertEquals(1, len(t_v_ctxs))

        t_v_ctx = t_v_ctxs[0]
        self.assertEquals(t_id, t_v_ctx['tariff_id'])
        self.assertEquals(t_v_id, t_v_ctx['id'])
        self.assertEquals(t_v_name, t_v_ctx['name'])
        self.assertEquals(view_order, t_v_ctx['view_order'])
        self.assertEquals(context, t_v_ctx['context'])

    def test_get_tariff_viewing_contexts(self):
        t_id = self._add_tariff('t', currency='RUB')
        t_v_name = 'first'
        param_0 = {'name': 'num', 'value': 4}
        param_1 = {'name': 'param', 'value': 'like'}
        context = [param_0, param_1]
        view_order = 1
        t_v_id = self._add_tariff_viewing_context(t_v_name,
            t_id, context, view_order=view_order)

        l_t_v_ctxs = self._tariff_viewing_contexts_data(t_id)
        self.assertEquals(1, len(l_t_v_ctxs))
        d_t_v_ctx = l_t_v_ctxs[0]

        self.assertEquals(d_t_v_ctx['id'], t_v_id)
        self.assertEquals(d_t_v_ctx['name'], t_v_name)
        self.assertEquals(d_t_v_ctx['tariff_id'], t_id)
        self.assertEquals(d_t_v_ctx['view_order'], view_order)

        act_context = d_t_v_ctx['context']
        self.assertEquals(len(act_context), len(context))
        self.assertTrue(param_0 in act_context)
        self.assertTrue(param_1 in act_context)


if __name__ == '__main__':
    unittest.main()