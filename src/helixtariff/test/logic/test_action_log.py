# coding=utf-8
import unittest

from helixcore.test.utils_for_testing import ActionsLogTester
#from helixcore.security.auth import CoreAuthenticator
#from helixcore.test.logic.access_granted import (access_denied_call,
#    access_granted_call)

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixtariff.test.wsgi.client import Client
from helixtariff.db.dataobject import Tariff, Rule


class ActionLogTestCase(ActorLogicTestCase, ActionsLogTester):
    sess_id = 'action_log_test_session'

    def setUp(self):
        super(ActionLogTestCase, self).setUp()
        self.cli = Client()

    def test_ping(self):
        action = 'ping'
        req = {}
        self._not_logged_action(action, self.sess_id, req)

    def test_add_tariffication_object(self):
        action = 'add_tariffication_object'
        req = {'session_id': self.sess_id, 'name': 'one'}
        self._logged_action(action, req)

    def test_modify_tariffication_object(self):
        action = 'add_tariffication_object'
        req = {'session_id': self.sess_id, 'name': 'one'}
        resp = self._logged_action(action, req)
        to_id = resp['id']

        action = 'modify_tariffication_object'
        req = {'session_id': self.sess_id, 'new_name': 'ttt_one', 'id': to_id}
        resp = self._logged_action(action, req)

    def test_delete_tariffication_object(self):
        action = 'add_tariffication_object'
        req = {'session_id': self.sess_id, 'name': 'one'}
        resp = self._logged_action(action, req)
        to_id = resp['id']

        action = 'delete_tariffication_object'
        req = {'session_id': self.sess_id, 'id': to_id}
        resp = self._logged_action(action, req)

    def test_get_tariffication_object(self):
        action = 'get_tariffication_objects'
        self._not_logged_filtering_action(action, self.sess_id)

    def test_add_tariff(self):
        action = 'add_tariff'
        req = {'session_id': self.sess_id, 'name': 't', 'parent_tariff_id': None,
            'status': Tariff.STATUS_ACTIVE, 'type': Tariff.TYPE_PERSONAL,
            'currency': 'RUB'}
        self._logged_action(action, req)

    def test_delete_tariff(self):
        action = 'add_tariff'
        req = {'session_id': self.sess_id, 'name': 't', 'parent_tariff_id': None,
            'status': Tariff.STATUS_ACTIVE, 'type': Tariff.TYPE_PERSONAL,
            'currency': 'RUB'}
        resp = self._logged_action(action, req)
        t_id = resp['id']

        action = 'delete_tariff'
        req = {'session_id': self.sess_id, 'id': t_id}
        self._logged_action(action, req)

    def test_modify_tariff(self):
        action = 'add_tariff'
        req = {'session_id': self.sess_id, 'name': 't', 'parent_tariff_id': None,
            'status': Tariff.STATUS_ACTIVE, 'type': Tariff.TYPE_PERSONAL,
            'currency': 'RUB'}
        resp = self._logged_action(action, req)
        t_id = resp['id']

        action = 'modify_tariff'
        req = {'session_id': self.sess_id, 'id': t_id, 'new_name': 'tt'}
        self._logged_action(action, req)

    def test_save_rule(self):
        to_id = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t0', currency='RUB')

        action = 'save_rule'
        req = {'session_id': self.sess_id, 'tariff_id': t_id, 'tariffication_object_id': to_id,
            'draft_rule': 'price = 11', 'status': Rule.STATUS_ACTIVE}
        self._logged_action(action, req)

    def test_apply_draft_rules(self):
        to_id = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t0', currency='RUB')
        self._save_rule(t_id, to_id, 'price = 12')

        action = 'apply_draft_rules'
        req = {'session_id': self.sess_id, 'tariff_id': t_id}
        self._logged_action(action, req)

    def test_delete_rule(self):
        to_id = self._add_tariffication_object('to0')
        t_id = self._add_tariff('t0', currency='RUB')
        r_id = self._save_rule(t_id, to_id, 'price = 12')

        action = 'delete_rule'
        req = {'session_id': self.sess_id, 'id': r_id}
        self._logged_action(action, req)

    def test_add_user_tariff(self):
        t_id = self._add_tariff('t0', currency='RUB')
        u_id = 23

        action = 'add_user_tariff'
        req = {'session_id': self.sess_id, 'tariff_id': t_id, 'user_id': u_id}
        self._logged_action(action, req)
        self._check_subject_users_ids_set(self.sess_id, action, u_id)

    def test_delete_user_tariffs(self):
        t_id = self._add_tariff('t0', currency='RUB')
        u_id = 23

        action = 'delete_user_tariffs'
        req = {'session_id': self.sess_id, 'tariff_ids': [t_id], 'user_id': u_id}
        self._logged_action(action, req)
        self._check_subject_users_ids_set(self.sess_id, action, u_id)


if __name__ == '__main__':
    unittest.main()
