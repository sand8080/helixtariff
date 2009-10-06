from eventlet import api, util, wsgi
import cjson
import logging

from helixcore.server.api import Api as HelixApi
from helixcore.server.response import response_error, response_app_error
from helixcore.server.errors import RequestProcessingError

from helixtariff.conf import settings
from helixtariff.logic.actions import handle_action
from helixtariff.conf.log import logger
from helixtariff.validator.validator import validate

util.wrap_socket_with_coroutine_socket()

class Handler(object):
    def __init__(self):
        self.helix_api = HelixApi(validate)

    def __call__(self, environ, start_response):
        input = environ['eventlet.input']
        print

        raw_data = input.read()
        remote_addr = environ['REMOTE_ADDR'] if 'REMOTE_ADDR' in environ else 'undefined'
        logger.info('Request from %s' % remote_addr)
        logger.debug('Request from %s data %s' % (remote_addr, raw_data))

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
        self.log_response(remote_addr, response, response_ok)
        start_response('200 OK', [('Content-type', 'text/plain')])
        return [raw_response]

    def log_response(self, remote_addr, response, response_ok):
        level = logging.INFO if response_ok else logging.ERROR
        logger.log(level, 'Response to %s: %s' % (remote_addr, response))

    def adapt(self, obj, req):
        'Convert obj to bytes'
        req.write(str(obj))

class ServerLog(object):
    def write(self, s, l=0): #IGNORE:W0613
        logger.info('server: %s' % s)

def run():
    wsgi.server(
        api.tcp_listener((settings.server_http_addr, settings.server_http_port)),
        Handler(),
        max_size=5000,
        log=ServerLog()
    )

def run_ssl():
    raise NotImplementedError()
    wsgi.server(
        api.ssl_listener((settings.server_http_addr, settings.server_http_port)),
        Handler(),
        max_size=5000,
        log=ServerLog()
    )
