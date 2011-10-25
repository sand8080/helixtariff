import unittest

from helixcore.error import RequestProcessingError

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase


class UserTariffTestCase(ActorLogicTestCase):
    u_id = 22

    def test_add_user_tariff(self):
        t_id = self._add_tariff('tariff one')
        self._add_user_tariff(t_id, self.u_id)

    def test_add_user_tariff_duplication(self):
        name = 'tariff one'
        t_id = self._add_tariff(name)
        self._add_user_tariff(t_id, self.u_id)
        self.assertRaises(RequestProcessingError, self._add_user_tariff, t_id, self.u_id)

    def test_add_wrong_tariff(self):
        self.assertRaises(RequestProcessingError, self._add_user_tariff, 555, self.u_id)

#    def test_get_tariffs(self):
#        name_0 = 'tariff_0'
#        t_id_0 = self._add_tariff(name_0)
#
#        t_data = self._tariff_data(t_id_0)
#        self.assertEquals(t_id_0, t_data['id'])
#        self.assertEquals(name_0, t_data['name'])
#        self.assertEquals([], t_data['parent_tariffs'])
#
#        name_1 = 'tariff_1'
#        t_id_1 = self._add_tariff(name_1, parent_tariff_id=t_id_0)
#
#        t_data = self._tariff_data(t_id_1)
#        self.assertEquals(t_id_1, t_data['id'])
#        self.assertEquals(name_1, t_data['name'])
#        pts = t_data['parent_tariffs']
#        pts_0 = pts[0]
#        self.assertEquals(1, len(pts))
#        self.assertEquals(t_id_0, pts_0['id'])
#        self.assertEquals(name_0, pts_0['name'])
#
#    def test_modify_tariff(self):
#        pt_id = self._add_tariff('pt')
#        name, type, status  = 't', Tariff.TYPE_PERSONAL, Tariff.STATUS_ACTIVE
#        t_id = self._add_tariff(name, parent_tariff_id=pt_id,
#            type=type, status=status)
#
#        t_data = self._tariff_data(t_id)
#        self.assertEquals(name, t_data['name'])
#        self.assertEquals(pt_id, t_data['parent_tariffs'][0]['id'])
#        self.assertEquals(type, t_data['type'])
#        self.assertEquals(status, t_data['status'])
#
#        new_name = 'newt'
#        new_status = Tariff.STATUS_ARCHIVE
#        new_type = Tariff.TYPE_PUBLIC
#        new_pt_id = None
#        sess = self.login_actor()
#        req = {'session_id': sess.session_id, 'id': t_id,
#            'new_name': new_name, 'new_parent_tariff_id': new_pt_id,
#            'new_type': new_type, 'new_status': new_status}
#        resp = self.modify_tariff(**req)
#        self.check_response_ok(resp)
#
#        t_data = self._tariff_data(t_id)
#        self.assertEquals(new_name, t_data['name'])
#        self.assertEquals([], t_data['parent_tariffs'])
#        self.assertEquals(new_type, t_data['type'])
#        self.assertEquals(new_status, t_data['status'])
#
#    def test_tariff_cycle_detection(self):
#        pt_id = self._add_tariff('pt')
#        cht_id = self._add_tariff('cht', parent_tariff_id=pt_id)
#
#        sess = self.login_actor()
#        req = {'session_id': sess.session_id, 'id': pt_id,
#            'new_parent_tariff_id': cht_id}
#        self.assertRaises(RequestProcessingError, self.modify_tariff, **req)
#
#    def test_delete_tariff(self):
#        sess = self.login_actor()
#
#        t_id = self._add_tariff('t')
#        req = {'session_id': sess.session_id, 'filter_params': {'id': t_id},
#            'paging_params': {}}
#        resp = self.get_tariffs(**req)
#        self.check_response_ok(resp)
#        self.assertEquals(1, resp['total'])
#
#        req = {'session_id': sess.session_id, 'id': t_id}
#        resp = self.delete_tariff(**req)
#        self.check_response_ok(resp)
#        req = {'session_id': sess.session_id, 'filter_params': {'id': t_id},
#            'paging_params': {}}
#        resp = self.get_tariffs(**req)
#        self.check_response_ok(resp)
#        self.assertEquals(0, resp['total'])
#
#    def test_delete_used_tariff_failed(self):
#        pt_id = self._add_tariff('pt')
#        self._add_tariff('cht', parent_tariff_id=pt_id)
#
#        sess = self.login_actor()
#        req = {'session_id': sess.session_id, 'id': pt_id}
#        self.assertRaises(RequestProcessingError, self.delete_tariff, **req)


if __name__ == '__main__':
    unittest.main()