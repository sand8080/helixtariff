from helixcore.security import Session
import helixcore.test.logic.access_granted #@UnusedImport
from helixcore.test.logic.access_granted import (GRANTED_ENV_ID,
    GRANTED_USER_ID)

from helixtariff.test.logic.logic_test import LogicTestCase
from helixtariff.db.dataobject import Tariff, Rule


class ActorLogicTestCase(LogicTestCase):
    def login_actor(self):
        return Session('ACTOR_LOGIC_TEST_CASE', GRANTED_ENV_ID, GRANTED_USER_ID)

    def _add_tariff(self, name, parent_tariff_id=None, type=Tariff.TYPE_PUBLIC,
        status=Tariff.STATUS_ACTIVE, currency=None):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'name': name,
            'parent_tariff_id': parent_tariff_id,
            'type': type, 'status': status}
        if currency is not None:
            req['currency'] = currency
        resp = self.add_tariff(**req)
        self.check_response_ok(resp)
        return resp['id']

    def _add_tariff_viewing_context(self, name, tariff_id, context, view_order=0):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'name': name,
            'tariff_id': tariff_id, 'view_order': view_order,
            'context': context}
        resp = self.add_tariff_viewing_context(**req)
        self.check_response_ok(resp)
        return resp['id']

    def _add_user_tariff(self, tariff_id, user_id):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'user_id': user_id,
            'tariff_id': tariff_id}
        resp = self.add_user_tariff(**req)
        self.check_response_ok(resp)
        return resp['id']

    def _tariff_data(self, t_id):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'filter_params': {'id': t_id},
            'paging_params': {}}
        resp = self.get_tariffs(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, resp['total'])
        t_data = resp['tariffs'][0]
        return t_data

    def _add_tariffication_object(self, name):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'name': name}
        resp = self.add_tariffication_object(**req)
        self.check_response_ok(resp)
        return resp['id']

    def _save_rule(self, t_id, to_id, rule, status=Rule.STATUS_ACTIVE, id=None,
        view_order=None):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'tariff_id': t_id,
            'tariffication_object_id': to_id, 'draft_rule': rule,
            'status': status}
        if id is not None:
            req['id'] = id
        if view_order is not None:
            req['view_order'] = view_order
        resp = self.save_rule(**req)
        self.check_response_ok(resp)
        return resp['id']

    def _get_rules(self, ids):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'filter_params': {'ids': ids},
            'paging_params': {}, 'ordering_params': ['view_order']}
        resp = self.get_rules(**req)
        self.check_response_ok(resp)
        return resp['rules']

    def _get_price(self, t_id, to_id, calculation_ctx=None, user_id=None):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'tariff_id': t_id,
            'tariffication_object_id': to_id}
        if calculation_ctx is not None:
            req['calculation_context'] = calculation_ctx
        if user_id is not None:
            req['user_id'] = user_id
        resp = self.get_price(**req)
        self.check_response_ok(resp)
        return resp

    def _apply_draft_rules(self, t_id):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'tariff_id': t_id}
        resp = self.apply_draft_rules(**req)
        self.check_response_ok(resp)

    def _get_user_tariffs(self, user_ids, tariff_ids=None):
        sess = self.login_actor()
        f_params = {'user_ids': user_ids}
        if tariff_ids is not None:
            f_params['tariff_ids'] = tariff_ids
        req = {'session_id': sess.session_id, 'filter_params': f_params,
            'paging_params': {}}
        resp = self.get_user_tariffs(**req)
        self.check_response_ok(resp)
        return resp['user_tariffs']

