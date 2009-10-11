import urllib2
import random
import cjson

def random_syllable(
    consonant='r|t|p|l|k|ch|kr|ts|bz|dr|zh|g|f|d|s|z|x|b|n|m'.split('|'),
    vowels='eyuioja'
):
    return ''.join(map(random.choice, (consonant, vowels)))


def random_word(min_syllable=2, max_syllable=6):
    return ''.join(random_syllable() for x in range(random.randint(min_syllable, max_syllable))) #@UnusedVariable


class Client(object):
    def __init__(self, host, port, login, password):
        self.host = host
        self.port = port
        self.login = login
        self.password = password

    def request(self, data):
        req = urllib2.Request(url='http://%s:%d' % (self.host, self.port), data=cjson.encode(data))
        f = urllib2.urlopen(req)
        return f.read()

    def ping(self):
        return self.request({'action': 'ping'})

    def add_client(self):
        return self.request({'action': 'add_client', 'login': self.login,
            'password': self.password})

    def add_service_type(self, name):
        return self.request({'action': 'add_service_type', 'login': self.login,
            'password': self.password, 'name': name})

    def add_service_set_descr(self, name):
        return self.request({'action': 'add_service_set_descr', 'login': self.login, 'password': self.password,
            'name': name})

    def add_to_service_set(self, name, types):
        return self.request({'action': 'add_to_service_set', 'login': self.login, 'password': self.password,
            'name': name, 'types': types})

    def add_tariff(self, name, service_set_descr_name):
        return self.request({'action': 'add_tariff', 'login': self.login, 'password': self.password,
            'name': name, 'service_set_descr_name': service_set_descr_name, 'in_archive': False})

    def get_tariff_detailed(self, name):
        response = cjson.decode(
            self.request({'action': 'get_tariff_detailed', 'login': self.login, 'name': name})
        )
        return response['tariff']

    def add_rule(self, tariff_name, service_type_name, rule):
        return self.request({'action': 'add_rule', 'login': self.login, 'password': self.password,
            'tariff_name': tariff_name, 'service_type_name': service_type_name, 'rule': rule})

    def get_price(self, tariff_name, service_type_name):
        return self.request({'action': 'get_domain_service_price', 'login': self.login,
            'tariff_name': tariff_name, 'service_type_name': service_type_name})
