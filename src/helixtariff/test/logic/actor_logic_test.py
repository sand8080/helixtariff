from helixcore.security import Session
import helixcore.test.logic.access_granted #@UnusedImport
from helixcore.test.logic.access_granted import (GRANTED_ENV_ID,
    GRANTED_USER_ID)

from helixtariff.test.logic.logic_test import LogicTestCase
from helixtariff.db.dataobject import Tariff


class ActorLogicTestCase(LogicTestCase):
    def login_actor(self):
        return Session('ACTOR_LOGIC_TEST_CASE', GRANTED_ENV_ID, GRANTED_USER_ID)

    def _add_tariff(self, name, parent_tariff_id=None, type=Tariff.TYPE_PUBLIC,
        status=Tariff.STATUS_ACTIVE):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'name': name,
            'parent_tariff_id': parent_tariff_id,
            'type': type, 'status': status}
        resp = self.add_tariff(**req)
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
