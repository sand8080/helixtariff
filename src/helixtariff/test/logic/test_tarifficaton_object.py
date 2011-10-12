# coding=utf-8
import unittest

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixcore.error import RequestProcessingError


class TarifficationObjectTestCase(ActorLogicTestCase):
    def _add_tariffication_object(self, name):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'name': name}
        resp = self.add_tariffication_object(**req)
        self.check_response_ok(resp)
        return resp['id']

    def test_add_tariffication_object(self):
        self._add_tariffication_object('Product one')
        self._add_tariffication_object(u'маринад')

    def test_add_tariffication_object_duplication(self):
        name = u'тесто'
        self._add_tariffication_object(name)
        self.assertRaises(RequestProcessingError, self._add_tariffication_object, name)

    def test_get_tariffication_objects(self):
        prods = ['one', 'two', 'three']
        for prod in prods:
            self._add_tariffication_object(prod)

        resp = self._get_tariffication_objects()
        self.assertEquals(len(prods), resp['total'])
        for d in resp['tariffication_objects']:
            self.assertTrue(d['name'] in prods)

    def test_modify_tariffication_object(self):
        name ='one'
        to_id = self._add_tariffication_object(name)

        sess = self.login_actor()
        new_name = 'new_%s' % name
        req = {'session_id': sess.session_id, 'id': to_id,
            'new_name': new_name}
        resp = self.modify_tariffication_object(**req)
        self.check_response_ok(resp)

        resp = self._get_tariffication_objects(id=to_id)
        tos_data = resp['tariffication_objects']
        self.assertEquals(1, resp['total'])
        self.assertEquals(new_name, tos_data[0]['name'])

    def test_delete_tariffication_object(self):
        to_id = self._add_tariffication_object('one')

        resp = self._get_tariffication_objects()
        tos_num = resp['total']

        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'id': to_id}
        resp = self.delete_tariffication_object(**req)
        self.check_response_ok(resp)

        resp = self._get_tariffication_objects()
        new_tos_num = resp['total']
        self.assertEquals(tos_num - 1, new_tos_num)

        resp = self._get_tariffication_objects(id=to_id)
        self.assertEquals(0, len(resp['tariffication_objects']))

    def _get_tariffication_objects(self, id=None):
        sess = self.login_actor()
        filter_params = {}
        if id:
            filter_params['id'] = id
        req = {'session_id': sess.session_id, 'filter_params': filter_params,
            'paging_params': {}}
        resp = self.get_tariffication_objects(**req)
        self.check_response_ok(resp)
        return resp


if __name__ == '__main__':
    unittest.main()