from decimal import Decimal, InvalidOperation

from helixtariff.error import RuleProcessingError
from helixtariff.rulesengine.checker import RuleChecker


class RequestPrice(object):
    def __init__(self, rule_text, **kwargs):
        self.rule = rule_text
        self.objects_num = 1
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.__dict__)


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

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.__dict__)


def process(request):
    price = None
    checker = RuleChecker()
    checker.check(request.rule)
    exec request.rule
    return ResponsePrice(price)
