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


class CurrencyNotFound(HelixtariffObjectNotFound):
    def __init__(self, **kwargs):
        super(CurrencyNotFound, self).__init__('Currency', **kwargs)


class TarifficationObjectNotFound(HelixtariffObjectNotFound):
    def __init__(self, **kwargs):
        super(TarifficationObjectNotFound, self).__init__('TarifficationObject', **kwargs)
        self.code = error_code.HELIXTARIFF_TARIFFICATION_OBJECT_NOT_FOUND


class TarifficationObjectAlreadyExsits(HelixtariffObjectAlreadyExists):
    def __init__(self, name):
        super(TarifficationObjectAlreadyExsits, self).__init__('%s already exists' % name)
        self.code = error_code.HELIXTARIFF_TARIFFICATION_OBJECT_ALREADY_EXISTS


class TariffNotFound(HelixtariffObjectNotFound):
    def __init__(self, **kwargs):
        super(TariffNotFound, self).__init__('Tariff', **kwargs)
        self.code = error_code.HELIXTARIFF_TARIFF_NOT_FOUND


class TariffViewingContextNotFound(HelixtariffObjectNotFound):
    def __init__(self, **kwargs):
        super(TariffViewingContextNotFound, self).__init__('TariffViewingContext', **kwargs)
        self.code = error_code.HELIXTARIFF_TARIFF_NOT_FOUND


class ParentTariffWithoutCurrency(HelixtariffError):
    code = error_code.HELIXTARIFF_PARENT_TARIFF_WITHOUT_CURRENCY


class NonParentTariffWithCurrency(HelixtariffError):
    code = error_code.HELIXTARIFF_NON_PARENT_TARIFF_WITH_CURRENCY


class UserTariffAlreadyExsits(HelixtariffObjectAlreadyExists):
    def __init__(self, tariff_id=None, user_id=None):
        super(UserTariffAlreadyExsits, self).__init__('User tariff %s already exists for user %s' %
            (tariff_id, user_id))
        self.code = error_code.HELIXTARIFF_USER_TARIFF_ALREADY_EXISTS


class UserTariffNotFound(HelixtariffObjectNotFound):
    def __init__(self, **kwargs):
        super(UserTariffNotFound, self).__init__('Tariff', **kwargs)
        self.code = error_code.HELIXTARIFF_USER_TARIFF_NOT_FOUND


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
