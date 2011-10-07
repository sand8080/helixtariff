from helixcore.test.utils_for_testing import (ClientSimpleApplication, make_api_call,
    get_api_calls)

from helixtariff.conf.log import logger
from helixtariff.logic.actions import handle_action
from helixtariff.wsgi.protocol import protocol
from helixtariff.wsgi.server import HelixtariffApplication


class Client(ClientSimpleApplication):
    def __init__(self):
        app = HelixtariffApplication(handle_action, protocol, logger)
        super(Client, self).__init__(app)


for method_name in get_api_calls(protocol):
    setattr(Client, method_name, make_api_call(method_name))
