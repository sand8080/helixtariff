
from eventlet import api, httpd, util
import logging

from helixbilling.conf.settings import server_http_addr, server_http_port

from helixcore.server.api.api import Api as HelixApi
from helixbilling.logic.actions import handle_action
from helixbilling.logic.response import response_error, response_app_error
from helixbilling.error.errors import RequestProcessingError
from helixbilling.conf.log import logger
from helixbilling.validator.validator import validate

util.wrap_socket_with_coroutine_socket()

class Handler(object):
    def __init__(self):
        self.helix_api = HelixApi(validate)

    def handle_request(self, req):

        raw_data = req.read_body()
        logger.info('HTTP req from %s: %s' % (str(req.socket().getpeername()), raw_data))

        response_ok = False
        try:
            action_name, data = self.helix_api.handle_request(raw_data)
            response = handle_action(action_name, data)
            response_ok = True
        except RequestProcessingError, e:
            response = response_error(e)
        except Exception, e:
            response = response_app_error(e.message)

        raw_response = self.helix_api.handle_response(response)

        self.log_response(req, response_ok, raw_response)
        req.response(200, body=raw_response)

    def log_response(self, req, response_ok, raw_response):
        level = response_ok and logging.INFO or logging.ERROR
        logger.log(level, 'HTTP response to %s: %s' % (str(req.socket().getpeername()), raw_response))

    def adapt(self, obj, req):
        'Convert obj to bytes'
        req.write(str(obj))

def run():
    class ServerLog(object):
        def write(self, s, l=0): #IGNORE:W0613
            logger.info('server: %s' % s)

    #blocking
    httpd.server(api.tcp_listener((server_http_addr, server_http_port)), Handler(), max_size=5000, log=ServerLog())
