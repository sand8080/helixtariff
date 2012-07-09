from helixtariff.conf.log import logger
from helixtariff.logic.actions import handle_action
from helixtariff.wsgi.protocol import protocol
from helixtariff.wsgi.application import HelixtariffApplication


application = HelixtariffApplication(handle_action, protocol, logger)
