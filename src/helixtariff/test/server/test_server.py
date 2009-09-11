import unittest
import httplib
import cjson
from threading import Thread
from time import sleep

from helixbilling.test.root_test import RootTestCase
from helixbilling.conf.settings import server_http_addr, server_http_port
from helixbilling.server.http import run

class ServerTestCase(RootTestCase):

    def test_ping_ok(self):
        t = Thread(target=run)
        t.setDaemon(True)
        t.start()

        sleep(0.5)
        request_data = {'action': 'ping'}

        conn = httplib.HTTPConnection(server_http_addr, server_http_port)
        conn.request('POST', '/', cjson.encode(request_data))

        response_obj = conn.getresponse()
        self.assertTrue(response_obj.status, 200)

        raw_response = response_obj.read()
        response_data = cjson.decode(raw_response)

        self.assertTrue(response_data['status'], 'ok')

if __name__ == '__main__':
    unittest.main()
