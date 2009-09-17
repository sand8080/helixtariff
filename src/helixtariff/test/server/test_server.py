import unittest
import httplib
import cjson
from threading import Thread

from helixtariff.test.root_test import RootTestCase
from helixtariff.conf.settings import server_http_addr, server_http_port
from helixtariff.server.http import run

t = Thread(target=run)
t.setDaemon(True)
t.start()

class ServerTestCase(RootTestCase):
    def test_ping_ok(self):
        request_data = {'action': 'ping'}

        conn = httplib.HTTPConnection(server_http_addr, server_http_port)
        conn.request('POST', '/', cjson.encode(request_data))

        response_obj = conn.getresponse()

        self.assertTrue(response_obj.status, 200)

        raw_response = response_obj.read()
        response_data = cjson.decode(raw_response)

        self.assertTrue(response_data['status'], 'ok')

    def test_invalid_request(self):
        request_data = {'action': 'fakeaction'}

        conn = httplib.HTTPConnection(server_http_addr, server_http_port)
        conn.request('POST', '/', cjson.encode(request_data))

        response_obj = conn.getresponse()

        self.assertTrue(response_obj.status, 200)

        raw_response = response_obj.read()
        response_data = cjson.decode(raw_response)

        self.assertTrue(response_data['status'], 'error')
        self.assertTrue(response_data['category'], 'validation')


if __name__ == '__main__':
    unittest.main()
