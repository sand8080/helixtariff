from helixtariff.conf import settings
settings.DSN = 'dbname=test_helixtariff host=localhost user=helixtest password=qazwsx'

import logging
settings.log_filename = '/tmp/helixtariff.log'
settings.log_level = logging.DEBUG
settings.log_console = True

import os
patches_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), '..', '..', 'patches')
