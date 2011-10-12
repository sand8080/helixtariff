import unittest

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixtariff.db.dataobject import Tariff
from helixcore.error import RequestProcessingError


class TariffTestCase(ActorLogicTestCase):
    def _add_tariffication_object(self, name):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'name': name}
        resp = self.add_tariffication_object(**req)
        self.check_response_ok(resp)
        return resp['id']

    def _add_tariff(self, name, parent_tariff_id=None, tariffication_objects_ids=None,
        type=Tariff.TYPE_PUBLIC):
        if tariffication_objects_ids is None:
            tariffication_objects_ids = []
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'name': name,
            'parent_tariff_id': parent_tariff_id,
            'type': type, 'status': Tariff.STATUS_ACTIVE,
            'tariffication_objects_ids': tariffication_objects_ids}
        resp = self.add_tariff(**req)
        self.check_response_ok(resp)

    def test_add_tariff(self):
        to_id = self._add_tariffication_object('product one')
        self._add_tariff('tariff one', tariffication_objects_ids=[to_id])

    def test_add_tariff_duplication(self):
        name = 'tariff one'
        self._add_tariff(name)
        self.assertRaises(RequestProcessingError, self._add_tariff, name)

    def test_same_name_tariffs_but_different_types_accepted(self):
        name = 'tariff same'
        self._add_tariff(name, type=Tariff.TYPE_PERSONAL)
        self._add_tariff(name, type=Tariff.TYPE_PUBLIC)

    def test_add_parent_tariff(self):
        t_id = self._add_tariff('tariff parent')
        self._add_tariff('tariff child', t_id)

    def test_add_wrong_parent_tariff(self):
        self.assertRaises(RequestProcessingError, self._add_tariff, 'tariff one',
            {'parent_tariff_id': 4444})

    def test_only_exist_tariffication_objects_saved(self):
        to_id = self._add_tariffication_object('product one')
        t_id = self._add_tariff('tariff one',
            tariffication_objects_ids=[to_id, 33, 44, 55])

        # TODO: implement checking by get action



if __name__ == '__main__':
    unittest.main()