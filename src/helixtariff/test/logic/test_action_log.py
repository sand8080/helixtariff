# coding=utf-8
import unittest

from helixcore.test.utils_for_testing import ActionsLogTester
from helixcore.security.auth import CoreAuthenticator
from helixcore.test.logic.access_granted import (access_denied_call,
    access_granted_call)

from helixtariff.test.logic.actor_logic_test import ActorLogicTestCase
from helixtariff.test.wsgi.client import Client


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


#
#    def test_unauthorized_tracking_action(self):
#        self.cli.add_operator(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
#        self._check_action_tracked(self.get_operator_by_login(self.cli.login), 'add_operator', None)
#
#    def test_tracking_error_action(self):
#        custom_operator_info = 'fake'
#        self.cli.add_operator(custom_operator_info=custom_operator_info) #IGNORE:E1101
#        operator = self.get_operator_by_login(self.cli.login)
#        self._check_action_tracked(operator, 'add_operator', custom_operator_info)
#        self._make_trackable_action(operator, 'modify_service_type', {'name': 'fake', 'new_name': 'ff'})
#
#    def test_tracking_action(self):
#        self.cli.add_operator(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
#        operator = self.get_operator_by_login(self.cli.login)
#
#        self._make_trackable_action(operator, 'modify_operator', {'custom_operator_info': 'jah'})
#
#        old_st_name = 'service type'
#        self._make_trackable_action(operator, 'add_service_type', {'name': old_st_name})
#        st_name = 'new %s' % old_st_name
#        self._make_trackable_action(operator, 'modify_service_type', {'name': old_st_name,
#            'new_name': st_name})
#
#        old_ss_name = 'service set'
#        self._make_trackable_action(operator, 'add_service_set', {'name': old_ss_name,
#            'service_types': [st_name]})
#        ss_name = 'new %s' % old_ss_name
#        self._make_trackable_action(operator, 'modify_service_set', {'name': old_ss_name,
#            'new_name': ss_name})
#
#        old_t_name = 'tariff'
#        self._make_trackable_action(operator, 'add_tariff', {'name': old_t_name,
#            'parent_tariff': None, 'service_set': ss_name, 'in_archive': False})
#        t_name = 'new %s' % old_t_name
#        self._make_trackable_action(operator, 'modify_tariff', {'name': old_t_name,
#            'new_name': t_name, 'new_in_archive': True})
#
#        r_text = 'price = 1.0'
#        self._make_trackable_action(operator, 'save_draft_rule', {'tariff': t_name,
#            'service_type': st_name, 'rule': r_text, 'enabled': True})
#        self._make_trackable_action(operator, 'make_draft_rules_actual', {'tariff': t_name})
#        self._make_trackable_action(operator, 'modify_actual_rule', {'tariff': t_name,
#            'service_type': st_name, 'new_enabled': False})
#
#        self._make_trackable_action(operator, 'delete_tariff', {'name': t_name})
#        self.cli.modify_service_set(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
#            name=ss_name, new_service_types=[])
#        self._make_trackable_action(operator, 'delete_service_set', {'name': ss_name})
#        self._make_trackable_action(operator, 'delete_service_type', {'name': st_name})
#
#    def test_view_action_logs(self):
#        self.cli.add_operator(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
#
#        st_names = ['st 0', 'st 1', 'st 2']
#        date_0 = datetime.datetime.now(pytz.utc)
#        for st_name in st_names:
#            self._make_action('add_service_type', {'name': st_name})
#
#        ss_names = ['ss 0', 'ss 1']
#        date_1 = datetime.datetime.now(pytz.utc)
#        for ss_name in ss_names:
#            self._make_action('add_service_set', {'name': ss_name,
#                'service_types': st_names})
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        total = len(st_names) + len(ss_names) + 1
#        self.assertEqual(total, len(al_info))
#        self.assertEqual(total, response['total'])
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'action': 'add_service_type'},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        self.assertEqual(len(st_names), len(al_info))
#        self.assertEqual(0, len(filter(lambda x: x['action'] != 'add_service_type', al_info)))
#        self.assertEqual(len(st_names), response['total'])
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'action': 'add_service_type', 'limit': 2},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        self.assertEqual(2, len(al_info))
#        self.assertEqual(0, len(filter(lambda x: x['action'] != 'add_service_type', al_info)))
#        self.assertEqual(len(st_names), response['total'])
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'action': 'add_service_type', 'offset': 2},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        self.assertEqual(1, len(al_info))
#        self.assertEqual(0, len(filter(lambda x: x['action'] != 'add_service_type', al_info)))
#        self.assertEqual(len(st_names), response['total'])
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'from_date': date_1.isoformat()},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        self.assertEqual(len(ss_names), len(al_info))
#        self.assertEqual(0, len(filter(lambda x: x['action'] != 'add_service_set', al_info)))
#        self.assertEqual(len(ss_names), response['total'])
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'from_date': date_0.isoformat(), 'to_date': date_1.isoformat()},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        self.assertEqual(len(st_names), len(al_info))
#        self.assertEqual(0, len(filter(lambda x: x['action'] != 'add_service_type', al_info)))
#        self.assertEqual(len(st_names), response['total'])


if __name__ == '__main__':
    unittest.main()
