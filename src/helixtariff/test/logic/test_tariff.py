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

#    def test_add_tariff_duplication(self):
#        name = 'tariff one'
#        self._add_tariff(name)
#        self.assertRaises(RequestProcessingError, self._add_tariff, name)
#
#    def test_same_name_tariffs_but_different_types_accepted(self):
#        name = 'tariff same'
#        self._add_tariff(name, type=Tariff.TYPE_PERSONAL)
#        self._add_tariff(name, type=Tariff.TYPE_PUBLIC)
#
#    def test_add_parent_tariff(self):
#        t_id = self._add_tariff('tariff parent')
#        self._add_tariff('tariff child', t_id)
#
#        # TODO: implement checking by get action
#
#    def test_add_wrong_parent_tariff(self):
#        self.assertRaises(RequestProcessingError, self._add_tariff, 'tariff one',
#            {'parent_tariff_id': 4444})
#
#    def test_only_exist_tariffication_objects_saved(self):
#        to_id = self._add_tariffication_object('product one')
#        t_id = self._add_tariff('tariff one',
#            tariffication_objects_ids=[to_id, 33, 44, 55])
#
#        # TODO: implement checking by get action

#    def test_get_tariffs(self):
#        to_id_0 = self._add_tariffication_object('p0')
#        to_id_1 = self._add_tariffication_object('p1')
#        t_id = self._add_tariff('tariff one',
#            tariffication_objects_ids=[to_id_0, to_id_1])
#
#        sess = self.login_actor()
#        req = {'session_id': sess.session_id, 'filter_params': {'id': t_id},
#            'paging_params': {}}
#        resp = self.get_tariffs(**req)
#        self.check_response_ok(resp)
#        self.assertEquals(1, resp['total'])
#        t_data = resp['tariffs'][0]
#        self.assertEquals(t_id, t_data['id'])
#        self.assertEquals([{'tariff_id': 1, 'id': 1, 'name': u'p0'},
#            {'tariff_id': 1, 'id': 2, 'name': u'p1'}],
#            t_data['tariffication_objects'])
#
#        t_id = self._add_tariff('tariff two', parent_tariff_id=t_id,
#            tariffication_objects_ids=[to_id_0])
#        req = {'session_id': sess.session_id, 'filter_params': {'id': t_id},
#            'paging_params': {}}
#        resp = self.get_tariffs(**req)
#        self.check_response_ok(resp)
#        self.assertEquals(1, resp['total'])
#        t_data = resp['tariffs'][0]
#        self.assertEquals(t_id, t_data['id'])
#        print '### resp'


if __name__ == '__main__':
    unittest.main()