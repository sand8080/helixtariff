#import logging
import logging.handlers
from settings import log_filename, log_level, log_console, log_format

def init_logger():
    l = logging.getLogger('helixtariff')
    l.setLevel(log_level)

    fmt = logging.Formatter(log_format)

    file_handler = logging.handlers.RotatingFileHandler(log_filename, mode='a', maxBytes=2000000,
        backupCount=10, encoding='UTF-8')
    file_handler.setFormatter(fmt)

    l.addHandler(file_handler)

    if log_console:
        cons_handler = logging.StreamHandler()
        cons_handler.setLevel(log_level)
        cons_handler.setFormatter(fmt)
        l.addHandler(cons_handler)
    return l

logger = init_logger()
