from helixtariff.conf import settings

settings.DSN = {
    'user': 'helixtest',
    'database': 'test_helixtariff',
    'host': 'localhost',
    'password': 'qazwsx'
}

settings.server_host = 'localhost'
settings.server_port = 10999

import os
current_dir = os.path.realpath(os.path.dirname(__file__))
patches_path = os.path.join(current_dir, '..', '..', 'patches')

import logging
settings.log_filename = '/tmp/helixtariff.log'
settings.log_level = logging.DEBUG
settings.log_level = logging.INFO
settings.log_level = logging.ERROR
settings.log_console = True


from eventlet import api, util
util.wrap_socket_with_coroutine_socket()
import urllib2
from helixtariff.wsgi.server import Server
from helixtariff.test.wsgi.client import Client


def start_server():
    cli = Client(settings.server_host, settings.server_port, '', '')
    try:
        cli.ping() #IGNORE:E1101
    except urllib2.URLError:
        api.spawn(Server.run)
    cli.ping() #IGNORE:E1101



