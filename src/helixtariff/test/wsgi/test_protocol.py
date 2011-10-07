# coding=utf-8
import unittest

from helixcore.server.api import Api
from helixcore.test.utils_for_testing import ProtocolTester

from helixtariff.test.root_test import RootTestCase
from helixtariff.wsgi.protocol import protocol
import datetime
import pytz


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
#
#    def test_get_currencies(self):
#        a_name = 'get_currencies'
#        self.api.validate_request(a_name, {'session_id': 's'})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'ordering_params': ['code']})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'ordering_params': ['-code']})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'currencies': []})
#        self.api.validate_response(a_name, {'status': 'ok', 'currencies': [
#            {'id': 1, 'code': 'YYY', 'name': 'y',
#                'location': 'y', 'cent_factor': 100}
#        ]})
#        self.validate_error_response(a_name)
#
#    def test_get_used_currencies(self):
#        a_name = 'get_used_currencies'
#        self.api.validate_request(a_name, {'session_id': 's'})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'ordering_params': ['code']})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'ordering_params': ['-code']})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'currencies': []})
#        self.api.validate_response(a_name, {'status': 'ok', 'currencies': [
#            {'id': 1, 'code': 'YYY', 'name': 'y',
#                'location': 'y', 'cent_factor': 100}
#        ]})
#        self.validate_error_response(a_name)
#
#    def test_modify_used_currencies(self):
#        a_name = 'modify_used_currencies'
#        self.api.validate_request(a_name, {'session_id': 's'})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'new_currencies_codes': []})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'new_currencies_codes': ['XXX', 'RUR', 'RUB']})
#
#        self.validate_status_response(a_name)
#
#    def test_get_action_logs(self):
#        a_name = 'get_action_logs'
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {}, 'paging_params': {},})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {}, 'paging_params': {'limit': 0,},})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {}, 'paging_params': {'limit': 0, 'offset': 0,},})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {'from_request_date': '2011-02-21 00:00:00',
#            'to_request_date': '2011-02-21 23:59:59'},
#            'paging_params': {}})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {'action': 'a'}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {'user_id': 1}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {'session_id': ''}, 'paging_params': {}})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
#            'action_logs': []})
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
#            'action_logs': [
#            {
#                'id': 42, 'session_id': 's_id', 'custom_actor_info': None,
#                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
#                'request_date': '%s' % datetime.datetime.now(pytz.utc),
#                'remote_addr': '127.0.0.1', 'request': 'req',
#                'response': 'resp'
#            },
#        ]})
#        self.validate_error_response(a_name)
#
#    def test_get_action_logs_self(self):
#        a_name = 'get_action_logs_self'
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {}, 'paging_params': {},})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {}, 'paging_params': {'limit': 0,},})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {}, 'paging_params': {'limit': 0, 'offset': 0,},})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {'from_request_date': '2011-02-21 00:00:00',
#            'to_request_date': '2011-02-21 23:59:59'},
#            'paging_params': {}})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {'action': 'a'}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'session_id': 's',
#            'filter_params': {'session_id': ''}, 'paging_params': {}})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
#            'action_logs': []})
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
#            'action_logs': [
#            {
#                'id': 42, 'session_id': 's_id', 'custom_actor_info': None,
#                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
#                'request_date': '%s' % datetime.datetime.now(pytz.utc),
#                'remote_addr': '127.0.0.1', 'request': 'req',
#                'response': 'resp'
#            },
#        ]})
#        self.validate_error_response(a_name)
#
#    def test_add_balance(self):
#        a_name = 'add_balance'
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'user_id': 23, 'currency_code': 'YYY'})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'user_id': 23, 'is_active': True, 'currency_code': 'YYY',
#            'overdraft_limit': '500.50'})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'user_id': 23, 'is_active': True, 'currency_code': 'YYY',
#            'overdraft_limit': '500.50'})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'user_id': 23, 'is_active': False, 'currency_code': 'YYY',
#            'overdraft_limit': '500.50'})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'user_id': 23, 'is_active': False, 'currency_code': 'YYY',
#            'overdraft_limit': '500.50'})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'user_id': 23, 'is_active': False, 'currency_code': 'YYY',
#            'overdraft_limit': '500.50', 'check_user_exist': True})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'id': 1})
#        self.validate_error_response(a_name)
#
#    def test_modify_balances(self):
#        a_name = 'modify_balances'
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'ids': [2], 'new_is_active': True,
#            'new_overdraft_limit': '500.50'})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'ids': [2, 3, 4], 'new_is_active': True,
#            'new_overdraft_limit': '500.50'})
#
#        self.validate_status_response(a_name)
#
#    def test_get_balances_self(self):
#        a_name = 'get_balances_self'
#        self.api.validate_request(a_name, {'session_id': 'i'})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'balances': [
#                {'id': 2, 'user_id': 3, 'is_active': True, 'currency_code': 'RUB',
#                'real_amount': '3.15', 'virtual_amount': '0.0',
#                'locked_amount': '14.09', 'overdraft_limit': '0.14',}
#            ],
#            'total': 1,
#        })
#        self.validate_error_response(a_name)
#
#    def test_get_balances(self):
#        a_name = 'get_balances'
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {}, 'paging_params': {},})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {},
#            'paging_params': {'limit': 0, 'offset': 0,}})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {'users_ids': [], 'is_active': True,
#            'currency_code': 'XXX',
#            'from_real_amount': '1.0',
#            'to_real_amount': '2.01',
#            'from_virtual_amount': '7.10',
#            'to_virtual_amount': '19.01',
#            'from_overdraft_limit': '600.17', 'to_overdraft_limit': '700',
#            'from_locked_amount': '41.24', 'to_locked_amount': '50',},
#            'paging_params': {}})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {'ids': [2, 3]}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {'id': 2}, 'paging_params': {},
#            'ordering_params': ['currency_id']})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
#            'balances': [
#                {
#                    'id': 22, 'user_id': 4, 'is_active': True,
#                    'currency_code': 'RU', 'real_amount': '3.15',
#                    'virtual_amount': '0.0',
#                    'locked_amount': '14.09', 'overdraft_limit': '0.14',
#                },
#            ]
#        })
#        self.validate_error_response(a_name)
#
#    def test_add_receipt(self):
#        a_name = 'add_receipt'
#        self.api.validate_request(a_name, {'session_id': 'i', 'balance_id': 23, 'amount': '44'})
#        self.api.validate_request(a_name, {'session_id': 'i', 'balance_id': 23, 'amount': '44.42',
#            'info': {'payment_system': 'YaD'}})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'transaction_id': 1})
#        self.validate_error_response(a_name)
#
#    def test_add_bonus(self):
#        a_name = 'add_bonus'
#        self.api.validate_request(a_name, {'session_id': 'i', 'balance_id': 23, 'amount': '44'})
#        self.api.validate_request(a_name, {'session_id': 'i', 'balance_id': 23, 'amount': '44.42',
#            'info': {'reason': 'beauty eyes'}})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'transaction_id': 1})
#        self.validate_error_response(a_name)
#
#    def test_lock(self):
#        a_name = 'lock'
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'balance_id': 23, 'amount': '44', 'order_id': 'o_44',
#            'locking_order': ['real_amount', 'virtual_amount']})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'balance_id': 23, 'amount': '44.42', 'order_id': 'o_45',
#            'locking_order': ['real_amount'], 'info': {'reason': 'beauty eyes'}})
#
#        self.api.validate_response(a_name, {'status': 'ok',
#            'transaction_id': 1, 'lock_id': 2})
#        self.validate_error_response(a_name)
#
#    def test_get_locks(self):
#        a_name = 'get_locks'
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {}, 'paging_params': {},})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {},
#            'paging_params': {'limit': 0, 'offset': 0,}})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {'id': 1, 'ids': [1, 2], 'user_id': 3,
#                'balance_id': 5, 'currency_code': 'XXX', 'order_id': 'o1',
#                'from_real_amount': '1.0', 'to_real_amount': '2.01',
#                'from_virtual_amount': '7.10', 'to_virtual_amount': '19.01',
#                'from_creation_date': '2011-02-21 00:00:00',
#                'to_creation_date': '2011-02-21 23:59:59',},
#            'paging_params': {}})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {'id': 2}, 'paging_params': {},
#            'ordering_params': ['id', '-id']})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
#            'locks': [
#                {
#                    'id': 22, 'user_id': 4, 'balance_id': 5, 'currency_code': 'RUB',
#                    'creation_date': '2011-02-21 00:00:00',
#                    'real_amount': '3.15', 'virtual_amount': '0.0',
#                    'info': {'p0': 'v0', 'p1': 'v1'}, 'order_id': 'o4'
#                },
#            ]
#        })
#        self.validate_error_response(a_name)
#
#    def test_get_locks_self(self):
#        a_name = 'get_locks_self'
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {}, 'paging_params': {},})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {},
#            'paging_params': {'limit': 0, 'offset': 0,}})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {'id': 1, 'ids': [1, 2],
#                'balance_id': 5, 'currency_code': 'XXX', 'order_id': 'o1',
#                'from_real_amount': '1.0', 'to_real_amount': '2.01',
#                'from_virtual_amount': '7.10', 'to_virtual_amount': '19.01',
#                'from_creation_date': '2011-02-21 00:00:00',
#                'to_creation_date': '2011-02-21 23:59:59',},
#            'paging_params': {}})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {'id': 2}, 'paging_params': {},
#            'ordering_params': ['id', '-id']})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
#            'locks': [
#                {
#                    'id': 22, 'user_id': 4, 'balance_id': 5, 'currency_code': 'RUB',
#                    'creation_date': '2011-02-21 00:00:00',
#                    'real_amount': '3.15', 'virtual_amount': '0.0',
#                    'info': {'p0': 'v0', 'p1': 'v1'}, 'order_id': '555'
#                },
#            ]
#        })
#        self.validate_error_response(a_name)
#
#    def test_unlock(self):
#        a_name = 'unlock'
#        self.api.validate_request(a_name, {'session_id': 'i', 'balance_id': 1,
#            'lock_id': 23})
#        self.api.validate_request(a_name, {'session_id': 'i', 'balance_id': 1,
#            'lock_id': 23, 'info': {'reason': 'order canceled'}})
#
#        self.api.validate_response(a_name, {'status': 'ok',
#            'transaction_id': 1})
#        self.validate_error_response(a_name)
#
#    def test_charge_off(self):
#        a_name = 'charge_off'
#        self.api.validate_request(a_name, {'session_id': 'i', 'balance_id': 1,
#            'lock_id': 23})
#        self.api.validate_request(a_name, {'session_id': 'i', 'balance_id': 1,
#            'lock_id': 23, 'info': {'reason': 'order canceled'}})
#
#        self.api.validate_response(a_name, {'status': 'ok',
#            'transaction_id': 1})
#        self.validate_error_response(a_name)
#
#    def test_get_transactions(self):
#        a_name = 'get_transactions'
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {}, 'paging_params': {},})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {},
#            'paging_params': {'limit': 0, 'offset': 0,}})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {'id': 1, 'ids': [1, 2],
#                'balance_id': 5, 'user_id': 3,
#                'from_creation_date': '2011-02-21 00:00:00',
#                'to_creation_date': '2011-02-21 23:59:59',
#                'type': 'charge_off'},
#            'paging_params': {}})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {'id': 2}, 'paging_params': {},
#            'ordering_params': ['id', '-id']})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
#            'transactions': [
#                {
#                    'id': 22, 'user_id': 4, 'balance_id': 5, 'currency_code': 'RUB',
#                    'creation_date': '2011-02-21 00:00:00',
#                    'real_amount': '3.15', 'virtual_amount': '0.0',
#                    'type': 'bonus', 'order_id': '5',
#                    'info': {'p0': 'v0', 'p1': 'v1'},
#                },
#            ]
#        })
#        self.validate_error_response(a_name)
#
#    def test_get_transactions_self(self):
#        a_name = 'get_transactions_self'
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {}, 'paging_params': {},})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {},
#            'paging_params': {'limit': 0, 'offset': 0,}})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {'id': 1, 'ids': [1, 2],
#                'balance_id': 5,
#                'from_creation_date': '2011-02-21 00:00:00',
#                'to_creation_date': '2011-02-21 23:59:59',
#                'type': 'charge_off'},
#            'paging_params': {}})
#        self.api.validate_request(a_name, {'session_id': 'i',
#            'filter_params': {'id': 2}, 'paging_params': {},
#            'ordering_params': ['id', '-id']})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
#            'transactions': [
#                {
#                    'id': 22, 'user_id': 4, 'balance_id': 5, 'currency_code': 'RUB',
#                    'creation_date': '2011-02-21 00:00:00',
#                    'real_amount': '3.15', 'virtual_amount': '0.0',
#                    'type': 'bonus', 'order_id': '5',
#                    'info': {'p0': 'v0', 'p1': 'v1'},
#                },
#            ]
#        })
#        self.validate_error_response(a_name)


if __name__ == '__main__':
    unittest.main()
