from eventlet import api, wsgi

from helixtariff.conf import settings
from helixtariff.wsgi.application import Handler
from helixtariff.conf.log import logger

class Server(object):
    class ServerLog(object):
        def write(self, s, l=0): #IGNORE:W0613
            logger.info('server: %s' % s)

    @staticmethod
    def run():
        wsgi.server(
            api.tcp_listener((settings.server_host, settings.server_port)),
            Handler(),
            max_size=5000,
            log=Server.ServerLog()
        )
