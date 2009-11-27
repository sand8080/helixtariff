from helixtariff.conf import settings

settings.DSN = {
    'user': 'helixtest',
    'database': 'helixtest',
    'host': 'localhost',
    'password': 'qazwsx'
}

import os
current_dir = os.path.realpath(os.path.dirname(__file__))
patches_path = os.path.join(current_dir, '..', '..', 'patches')

import logging
settings.log_filename = os.path.join(current_dir, '..', '..', '..', 'log', 'helixtariff.log')
settings.log_level = logging.DEBUG
settings.log_level = logging.INFO
settings.log_level = logging.ERROR
settings.log_console = True
