import json

from helixcore.server.api import Api
from helixcore.test.utils_for_testing import get_api_calls

# must be imported first in helixauth set
from helixtariff.test.db_based_test import DbBasedTestCase
from helixtariff.logic import actions
from helixtariff.wsgi.protocol import protocol


class LogicTestCase(DbBasedTestCase):
    def handle_action(self, action, data):
        api = Api(protocol)
        request = dict(data, action=action)
        action_name, data = api.handle_request(json.dumps(request))
        response = actions.handle_action(action_name, dict(data))
        api.handle_response(action_name, dict(response))
        return response

    def check_response_ok(self, resp):
        self.assertEqual('ok', resp['status'])


def make_api_call(f_name):
    def m(self, **kwargs):
        return self.handle_action(f_name, kwargs)
    m.__name__ = f_name
    return m


methods = get_api_calls(protocol)
for method_name in methods:
    setattr(LogicTestCase, method_name, make_api_call(method_name))
