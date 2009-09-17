from helixtariff.conf import settings
settings.DSN = 'dbname=test_helixtariff host=localhost user=helixtest password=qazwsx'

import os
current_dir = os.path.realpath(os.path.dirname(__file__))
patches_path = os.path.join(current_dir, '..', '..', 'patches')

import logging
settings.log_filename = os.path.join(current_dir, '..', '..', '..', 'log', 'helixtariff.log')
settings.log_level = logging.DEBUG
settings.log_console = True

