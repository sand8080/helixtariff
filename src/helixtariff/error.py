from helixtariff import error_code
from helixcore.db.wrapper import (ObjectCreationError, ObjectNotFound)
from helixcore import security


class HelixtariffError(Exception):
    code = error_code.HELIXTARIFF_ERROR


class HelixtariffObjectAlreadyExists(HelixtariffError, ObjectCreationError):
    def __init__(self, *args, **kwargs):
        super(HelixtariffObjectAlreadyExists, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXTARIFF_OBJECT_ALREADY_EXISTS


class HelixtariffObjectNotFound(HelixtariffError, ObjectNotFound):
    def __init__(self, class_name, **kwargs):
        sanitized_kwargs = security.sanitize_credentials(kwargs)
        super(HelixtariffObjectNotFound, self).__init__('%s not found by params: %s' %
            (class_name, sanitized_kwargs))
        self.code = error_code.HELIXTARIFF_OBJECT_NOT_FOUND


class TarifficationObjectNotFound(HelixtariffObjectNotFound):
    def __init__(self, **kwargs):
        super(TarifficationObjectNotFound, self).__init__('TarifficationObject', **kwargs)
        self.code = error_code.HELIXTARIFF_TARIFFICATION_OBJECT_NOT_FOUND


class TariffNotFound(HelixtariffObjectNotFound):
    def __init__(self, **kwargs):
        super(TariffNotFound, self).__init__('Tariff', **kwargs)
        self.code = error_code.HELIXTARIFF_TARIFF_NOT_FOUND


class TariffCycleDetected(HelixtariffError):
    code = error_code.HELIXTARIFF_TARIFF_CYCLE_DETECTED


class TariffUsed(HelixtariffError):
    code = error_code.HELIXTARIFF_TARIFF_USED


class RuleAlreadyExsits(HelixtariffObjectAlreadyExists):
    def __init__(self, rule):
        super(RuleAlreadyExsits, self).__init__('%s already exists' % rule)
        self.code = error_code.HELIXTARIFF_RULE_ALREADY_EXISTS


class RuleNotFound(HelixtariffObjectNotFound):
    def __init__(self, **kwargs):
        super(RuleNotFound, self).__init__('Rule', **kwargs)
        self.code = error_code.HELIXTARIFF_RULE_NOT_FOUND


class RuleProcessingError(HelixtariffError):
    code = error_code.HELIXTARIFF_RULE_PROCESSING_ERROR


class RuleCheckingError(HelixtariffError):
    code = error_code.HELIXTARIFF_RULE_CHECKING_ERROR


class PriceNotFound(HelixtariffError):
    code = error_code.HELIXTARIFF_PRICE_NOT_FOUND
