from helixtariff.error import HelixtariffError
from helixtariff.rulesengine.interaction import ResponsePrice
#from helixtariff.rulesengine.context import moc as context #IGNORE:W0611 @UnusedImport


class EngineError(HelixtariffError):
    pass


def process(request):
    price = None
    exec request.rule.rule #IGNORE:W0122
    return ResponsePrice(price)
