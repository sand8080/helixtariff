from helixcore.test.util import ClientApplication


class Client(ClientApplication):
    def __init__(self, host, port, login, password, protocol='http'):
        super(Client, self).__init__(host, port, login, password, protocol=protocol)


def make_api_call(f_name):
    def m(self, **kwargs):
        kwargs['action'] = f_name
        return self.request(kwargs)
    m.__name__ = f_name #IGNORE:W0621
    return m


for func_name in ['ping', 'add_client', 'add_service_type', 'add_service_set', 'add_to_service_set',
    'get_service_set', 'view_service_sets', 'add_tariff', 'get_tariff_detailed', 'view_tariffs',
    'view_detailed_tariffs', 'add_rule', 'get_price', 'view_prices', 'view_service_types',
    'view_rules',
    'incorect_error_message']:
    setattr(Client, func_name, make_api_call(func_name))
