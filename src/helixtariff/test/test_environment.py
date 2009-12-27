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
