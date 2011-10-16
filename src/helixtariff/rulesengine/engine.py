from decimal import Decimal, InvalidOperation

from helixtariff.error import RuleProcessingError
from helixtariff.rulesengine.checker import RuleChecker


class RequestPrice(object):
    def __init__(self, rule, context=None):
        context = {} if context is None else context
        self.rule = rule
        self.objects_num = 1
        for k, v in context:
            setattr(self, k, v)


class ResponsePrice(object):
    def __init__(self, price):
        if price is None:
            raise RuleProcessingError('Price not set in rule.')
        try:
            str_price = '%s' % price
            Decimal(str_price)
            self.price = str_price
        except (TypeError, InvalidOperation), e:
            raise RuleProcessingError(e)


def process(request):
    price = None
    rule = request.rule.rule
    checker = RuleChecker()
    checker.check(rule)
    exec rule
    return ResponsePrice(price)

