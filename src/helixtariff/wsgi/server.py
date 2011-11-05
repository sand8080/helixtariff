from eventlet import wsgi
from eventlet.green import socket

from helixtariff.conf import settings
from helixtariff.conf.log import logger
from helixtariff.logic.actions import handle_action
from helixtariff.wsgi.application import HelixtariffApplication
from helixtariff.wsgi.protocol import protocol


class Server(object):
    class ServerLog(object):
        def write(self, s, l=0): #IGNORE:W0613
            logger.log(l, 'server: %s' % s)

    @staticmethod
    def run():
        sock = socket.socket() #@UndefinedVariable
        sock.bind((settings.server_host, settings.server_port))
        sock.listen(settings.server_connections)
        logger.debug('Tariffication service started on %s:%s',
            settings.server_host, settings.server_port)
        wsgi.server(
            sock,
            HelixtariffApplication(handle_action, protocol, logger),
            max_size=5000,
            log=Server.ServerLog()
        )
