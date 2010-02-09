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


from helixtariff.wsgi.server import Server
from helixtariff.test.wsgi.client import Client
import threading
import time

def start_server():
    cli = Client(settings.server_host, settings.server_port, '', '')
    try:
        cli.ping() #IGNORE:E1101
    except Exception: #IGNORE:W0703
        t = threading.Thread(target=Server.run)
        t.start()
        time.sleep(1)
    cli.ping() #IGNORE:E1101



