from helixtariff.error import HelixtariffError
from helixtariff.rulesengine.interaction import (ResponsePrice,
    PriceProcessingError)
from helixtariff.rulesengine.checker import RuleChecker
#from helixtariff.rulesengine.context import moc as context #IGNORE:W0611 @UnusedImport


class EngineError(HelixtariffError):
    pass


def process(request):
    price = None
    rule = request.rule.rule
    checker = RuleChecker()
    checker.check(rule)
    try:
        exec rule #IGNORE:W0122
        return ResponsePrice(price)
    except KeyError, e:
        raise PriceProcessingError(e.message)

