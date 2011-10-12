# coding=utf-8
import unittest
import pytz
import datetime

from helixcore.server.api import Api
from helixcore.test.utils_for_testing import ProtocolTester

from helixtariff.test.root_test import RootTestCase
from helixtariff.wsgi.protocol import protocol
from helixtariff.db.dataobject import Tariff


class ProtocolTestCase(RootTestCase, ProtocolTester):
    api = Api(protocol)

    def test_login(self):
        a_name = 'login'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'environment_name': 'e', 'custom_actor_info': 'i'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'environment_name': 'n'})

        self.api.validate_response(a_name, {'status': 'ok', 'session_id': 'i',
            'user_id': 5, 'environment_id': 7})
        self.validate_error_response(a_name)

    def test_logout(self):
        a_name = 'logout'
        self.api.validate_request(a_name, {'session_id': 'i'})
        self.validate_status_response(a_name)

    def test_add_tariffication_object(self):
        a_name = 'add_tariffication_object'
        self.api.validate_request(a_name, {'session_id': 's', 'name': 'one'})
        self.api.validate_request(a_name, {'session_id': 's',
            'name': u'лунный свет'})
        self.api.validate_response(a_name, {'status': 'ok', 'id': 1})
        self.validate_error_response(a_name)

    def test_get_tariffication_objects(self):
        a_name = 'get_tariffication_objects'
        self.api.validate_request(a_name, {'session_id': 'i',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 'i',
            'filter_params': {'id': 1, 'ids': [1, 2], 'name': 'lala'},
            'paging_params': {'limit': 0, 'offset': 0,}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariffication_objects': [
                {'id': 1, 'name': 'one'},
                {'id': 2, 'name': 'two'},
            ]
        })
        self.validate_error_response(a_name)

    def test_modify_tariffication_object(self):
        a_name = 'modify_tariffication_object'
        self.api.validate_request(a_name, {'session_id': 's',
            'id': 1, 'new_name': 'one'})
        self.validate_status_response(a_name)

    def test_delete_tariffication_object(self):
        a_name = 'delete_tariffication_object'
        self.api.validate_request(a_name, {'session_id': 's', 'id': 1})
        self.validate_status_response(a_name)

    def test_get_action_logs(self):
        a_name = 'get_action_logs'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'from_request_date': '2011-02-21 00:00:00',
            'to_request_date': '2011-02-21 23:59:59'},
            'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'action': 'a'}, 'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'user_id': 1}, 'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'session_id': ''}, 'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'action_logs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'action_logs': [
            {
                'id': 42, 'session_id': 's_id', 'custom_actor_info': None,
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.1', 'request': 'req',
                'response': 'resp'
            },
        ]})
        self.validate_error_response(a_name)

    def test_get_action_logs_self(self):
        a_name = 'get_action_logs_self'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'from_request_date': '2011-02-21 00:00:00',
            'to_request_date': '2011-02-21 23:59:59'},
            'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'action': 'a'}, 'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'session_id': ''}, 'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'action_logs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'action_logs': [
            {
                'id': 42, 'session_id': 's_id', 'custom_actor_info': None,
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.1', 'request': 'req',
                'response': 'resp'
            },
        ]})
        self.validate_error_response(a_name)

    def test_add_tariff(self):
        a_name = 'add_tariff'
        self.api.validate_request(a_name, {'session_id': 's', 'name': 'one',
            'parent_tariff_id': None, 'tariffication_objects_ids': [],
            'type': 'public', 'status': 'active'})
        self.api.validate_request(a_name, {'session_id': 's', 'name': 'one',
            'parent_tariff_id': 1, 'tariffication_objects_ids': [1, 2],
            'type': 'public', 'status': 'archive'})

        self.api.validate_response(a_name, {'status': 'ok', 'id': 1})
        self.validate_error_response(a_name)

    def test_get_tariffs(self):
        a_name = 'get_tariffs'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'id': 1, 'ids': [1, 2], 'name': 't',
            'type': Tariff.TYPE_PERSONAL, 'status': Tariff.STATUS_ARCHIVE},
            'paging_params': {'limit': 0}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariffs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariffs': [
                {'id': 1, 'name': 't0', 'parent_tariffs': [{'id': 1, 'name': 'pt0'}],
                'tariffication_objects': [{'id': 1, 'name': 'item0', 'tariff_id': 2}],
                'type': Tariff.TYPE_PUBLIC, 'status': Tariff.STATUS_ACTIVE}
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'tariffs': [
                {'id': 1, 'name': 't0', 'parent_tariffs': [{'id': 2, 'name': 'pt2'}, {'id': 3, 'name': 'pt3'}],
                'tariffication_objects': [{'id': 1, 'name': 'item0', 'tariff_id': 2}],
                'type': Tariff.TYPE_PUBLIC, 'status': Tariff.STATUS_ACTIVE},
                {'id': 1, 'name': 't0', 'parent_tariffs': [{'id': 1, 'name': 'pt0'}],
                'tariffication_objects': [{'id': 1, 'name': 'item0', 'tariff_id': 2},
                    {'id': 2, 'name': 'item2', 'tariff_id': 3}],
                'type': Tariff.TYPE_PUBLIC, 'status': Tariff.STATUS_ACTIVE},
        ]})
        self.validate_error_response(a_name)


if __name__ == '__main__':
    unittest.main()
