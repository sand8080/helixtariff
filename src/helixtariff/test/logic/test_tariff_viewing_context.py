import unittest

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
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

    def test_modify_tariff_viewing_context_new_tariff_not_found(self):
        t_id = self._add_tariff('t', currency='RUB')
        t_v_name = 'first'
        context = [{'name': 'num', 'value': 4}]
        view_order = 1
        t_v_id = self._add_tariff_viewing_context(t_v_name,
            t_id, context, view_order=view_order)

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'id': t_v_id, 'new_tariff_id': 1900}
        self.assertRaises(RequestProcessingError, self.modify_tariff_viewing_context, **req)

    def test_modify_tariff_viewing_context_tariff_not_found(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'id': 1900}
        self.assertRaises(RequestProcessingError, self.modify_tariff_viewing_context,
            **req)

    def test_modify_tariff_viewing_context_tariff_no_modification(self):
        t_id = self._add_tariff('t', currency='RUB')
        context = [{'name': 'num', 'value': 4}]
        t_v_id = self._add_tariff_viewing_context('f', t_id, context, view_order=1)
        t_v_ctxs_exp = self._tariff_viewing_contexts_data(t_id)

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'id': t_v_id}
        resp = self.modify_tariff_viewing_context(**req)
        self.check_response_ok(resp)

        t_v_ctxs_act = self._tariff_viewing_contexts_data(t_id)
        self.assertEquals(t_v_ctxs_exp, t_v_ctxs_act)

    def test_modify_tariff_viewing_context_tariff_new_tariff(self):
        t_id = self._add_tariff('t', currency='RUB')
        ch_t_id = self._add_tariff('ch_t', parent_tariff_id=t_id)

        sess = self.login_actor()
        context = [{'name': 'num', 'value': 4}]
        t_v_id = self._add_tariff_viewing_context('f', t_id, context, view_order=1)
        req = {'session_id': sess.session_id, 'id': t_v_id, 'new_tariff_id': ch_t_id}
        resp = self.modify_tariff_viewing_context(**req)
        self.check_response_ok(resp)

        t_v_ctxs = self._tariff_viewing_contexts_data(ch_t_id)
        self.assertEquals(1, len(t_v_ctxs))
        t_v_ctx = t_v_ctxs[0]
        self.assertEquals(t_v_id, t_v_ctx['id'])
        self.assertEquals(ch_t_id, t_v_ctx['tariff_id'])

    def test_modify_tariff_viewing_context(self):
        t_id = self._add_tariff('t', currency='RUB')
        new_t_id = self._add_tariff('tt', currency='USD')

        sess = self.login_actor()
        context = [{'name': 'num', 'value': 4}]
        view_order = 1
        name = 'n'
        t_v_id = self._add_tariff_viewing_context(name, t_id, context,
            view_order=view_order)
        new_view_order = view_order + 1
        new_name = 'new_%s' % name
        new_context = [{'name': 'new', 'value': 5}]
        req = {'session_id': sess.session_id, 'id': t_v_id, 'new_tariff_id': new_t_id,
            'new_view_order': new_view_order, 'new_name': new_name,
            'new_context': new_context}
        resp = self.modify_tariff_viewing_context(**req)
        self.check_response_ok(resp)

        t_v_ctxs = self._tariff_viewing_contexts_data(new_t_id)
        self.assertEquals(1, len(t_v_ctxs))
        t_v_ctx = t_v_ctxs[0]
        self.assertEquals(t_v_id, t_v_ctx['id'])
        self.assertEquals(new_t_id, t_v_ctx['tariff_id'])
        self.assertEquals(new_name, t_v_ctx['name'])
        self.assertEquals(new_view_order, t_v_ctx['view_order'])
        self.assertEquals(new_context, t_v_ctx['context'])

    def test_delete_tariff_viewing_context_not_found(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'id': 1000}
        self.assertRaises(RequestProcessingError, self.delete_tariff_viewing_context,
            **req)

    def test_delete_tariff_viewing_context(self):
        t_id = self._add_tariff('t', currency='RUB')
        t_v_id = self._add_tariff_viewing_context('n', t_id, [])
        t_v_ctxs_before = self._tariff_viewing_contexts_data(t_id)

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'id': t_v_id}
        resp = self.delete_tariff_viewing_context(**req)
        self.check_response_ok(resp)

        t_v_ctxs_after = self._tariff_viewing_contexts_data(t_id)
        self.assertEquals(len(t_v_ctxs_before) - 1, len(t_v_ctxs_after))


if __name__ == '__main__':
    unittest.main()