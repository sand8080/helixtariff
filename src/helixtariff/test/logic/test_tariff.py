import unittest

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixtariff.db.dataobject import Tariff
from helixcore.error import RequestProcessingError


class TariffTestCase(ActorLogicTestCase):
    def _add_tariff(self, name, parent_tariff_id=None, type=Tariff.TYPE_PUBLIC):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'name': name,
            'parent_tariff_id': parent_tariff_id,
            'type': type, 'status': Tariff.STATUS_ACTIVE}
        resp = self.add_tariff(**req)
        self.check_response_ok(resp)
        return resp['id']

    def test_add_tariff(self):
        self._add_tariff('tariff one')

    def test_add_tariff_duplication(self):
        name = 'tariff one'
        self._add_tariff(name)
        self.assertRaises(RequestProcessingError, self._add_tariff, name)

    def test_add_parent_tariff(self):
        t_id = self._add_tariff('tariff parent')
        tch_id = self._add_tariff('tariff child', t_id)
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'filter_params': {'id': tch_id},
            'paging_params': {}}
        resp = self.get_tariffs(**req)
        self.check_response_ok(resp)
        t_data = resp['tariffs'][0]
        pts_data = t_data['parent_tariffs']
        self.assertEquals(1, len(pts_data))
        self.assertEquals(t_id, pts_data[0]['id'])


    def test_add_wrong_parent_tariff(self):
        self.assertRaises(RequestProcessingError, self._add_tariff, 'tariff one',
            {'parent_tariff_id': 4444})

    def test_get_tariffs(self):
        sess = self.login_actor()
        name_0 = 'tariff_0'
        t_id_0 = self._add_tariff(name_0)
        req = {'session_id': sess.session_id, 'filter_params': {'id': t_id_0},
            'paging_params': {}}
        resp = self.get_tariffs(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, resp['total'])
        t_data = resp['tariffs'][0]
        self.assertEquals(t_id_0, t_data['id'])
        self.assertEquals(name_0, t_data['name'])
        self.assertEquals([], t_data['parent_tariffs'])

        name_1 = 'tariff_1'
        t_id_1 = self._add_tariff(name_1, parent_tariff_id=t_id_0)
        req = {'session_id': sess.session_id, 'filter_params': {'id': t_id_1},
            'paging_params': {}}
        resp = self.get_tariffs(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, resp['total'])
        t_data = resp['tariffs'][0]
        self.assertEquals(t_id_1, t_data['id'])
        self.assertEquals(name_1, t_data['name'])
        pts = t_data['parent_tariffs']
        pts_0 = pts[0]
        self.assertEquals(1, len(pts))
        self.assertEquals(t_id_0, pts_0['id'])
        self.assertEquals(name_0, pts_0['name'])


if __name__ == '__main__':
    unittest.main()