import os
import logging

from helixtariff.conf import settings


settings.DSN = {
    'user': 'helixtest',
    'database': 'test_helixtariff',
    'host': 'localhost',
    'password': 'qazwsx'
}

settings.auth_server_url = 'http://localhost:10999'
settings.server_host = 'localhost'
settings.server_port = 10997

settings.log_filename = os.path.join(os.path.realpath(os.path.dirname(__file__)),
    'helixtariff.log')
settings.log_level = logging.DEBUG
settings.log_console = True
settings.auth_server_url = 'http://localhost:10999'

patches_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), '..', '..', 'patches')
