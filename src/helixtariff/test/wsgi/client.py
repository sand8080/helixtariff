from helixcore.test.util import ClientApplication

from helixtariff.conf.log import logger
from helixtariff.logic.actions import handle_action
from helixtariff.validator.validator import protocol
from helixtariff.wsgi.server import HelixtariffApplication


class Client(ClientApplication):
    def __init__(self, login, password):
        app = HelixtariffApplication(handle_action, protocol, logger)
        super(Client, self).__init__(app, login, password)


def make_api_call(f_name):
    def m(self, **kwargs):
        kwargs['action'] = f_name
        return self.request(kwargs)
    m.__name__ = f_name #IGNORE:W0621
    return m


for func_name in ['ping',
    'add_operator', 'modify_operator',
    'add_service_type', 'modify_service_type', 'delete_service_type', 'view_service_types',
    'add_service_set', 'modify_service_set', 'delete_service_set', 'get_service_set', 'view_service_sets',
    'add_tariff', 'modify_tariff', 'delete_tariff', 'get_tariff_detailed', 'view_tariffs', 'view_tariffs_detailed',
    'save_draft_rule', 'make_draft_rules_actual', 'modify_actual_rule', 'view_rules',
    'get_price', 'view_prices',
    'incorect_error_message']:
    setattr(Client, func_name, make_api_call(func_name))
