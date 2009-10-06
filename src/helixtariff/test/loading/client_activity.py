import urllib2
import cjson
from eventlet import api

import helixtariff.test.test_environment #IGNORE:W0611 @UnusedImport

from helixtariff.conf import settings
from helixtariff.server import http


class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def request(self, data):
        req = urllib2.Request(url='http://localhost:9998/fake/', data=cjson.encode(data))
        f = urllib2.urlopen(req)
        return f.read()

    def add_client(self, login, password):
        return self.request({'action': 'add_client', 'login': login, 'password': password})


if __name__ == '__main__':
    api.spawn(http.run)

    cli = Client(settings.server_http_addr, settings.server_http_port)
    resp = cli.add_client('wiki', 'qazwsx')
    print resp
