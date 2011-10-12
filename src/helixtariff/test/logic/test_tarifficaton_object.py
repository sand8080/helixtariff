# coding=utf-8
import unittest

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixcore.error import RequestProcessingError


class TarifficationObjectTestCase(ActorLogicTestCase):
    def test_add_tariffication_object(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'name': 'Product one'}
        resp = self.add_tariffication_object(**req)
        self.check_response_ok(resp)

        req = {'session_id': sess.session_id, 'name': u'маринад'}
        resp = self.add_tariffication_object(**req)
        self.check_response_ok(resp)

        # checking unique environment_id, name constraint
        req = {'session_id': sess.session_id, 'name': u'маринад'}
        self.assertRaises(RequestProcessingError, self.add_tariffication_object, **req)

    def test_get_tariffication_objects(self):
        sess = self.login_actor()
        prods = ['one', 'two', 'three']
        for prod in prods:
            req = {'session_id': sess.session_id, 'name': prod}
            resp = self.add_tariffication_object(**req)
            self.check_response_ok(resp)

        req = {'session_id': sess.session_id, 'filter_params': {},
            'paging_params': {}}
        resp = self.get_tariffication_objects(**req)
        self.check_response_ok(resp)
        self.assertEquals(len(prods), resp['total'])
        for d in resp['tariffication_objects']:
            self.assertTrue(d['name'] in prods)

    def test_modify_tariffication_object(self):
        sess = self.login_actor()
        name ='one'
        req = {'session_id': sess.session_id, 'name': name}
        resp = self.add_tariffication_object(**req)
        self.check_response_ok(resp)
        to_id = resp['id']

        new_name = 'new_%s' % name
        req = {'session_id': sess.session_id, 'id': to_id,
            'new_name': new_name}
        resp = self.modify_tariffication_object(**req)
        self.check_response_ok(resp)

        resp = self._get_tariffication_objects(id=to_id)
        tos_data = resp['tariffication_objects']
        self.assertEquals(1, len(tos_data))
        self.assertEquals(new_name, tos_data[0]['name'])

    def test_delete_tariffication_object(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'name': 'one'}
        resp = self.add_tariffication_object(**req)
        self.check_response_ok(resp)
        to_id = resp['id']

        resp = self._get_tariffication_objects()
        tos_num = len(resp['tariffication_objects'])

        req = {'session_id': sess.session_id, 'id': to_id}
        resp = self.delete_tariffication_object(**req)
        self.check_response_ok(resp)

        resp = self._get_tariffication_objects()
        new_tos_num = len(resp['tariffication_objects'])
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