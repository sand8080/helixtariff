from decimal import Decimal, InvalidOperation


class PriceProcessingError(Exception):
    pass


class RequestPrice(object):
    def __init__(self, rule, context=None):
        self.rule = rule
        self.context = {} if context is None else context

    def check_period(self, min_period=1, max_period=1):
        period = self.context.get('period')
        if period is None or period < min_period or period > max_period:
            raise PriceProcessingError('In rule %s period %s out of bounds: [%s, %s]' %
                (self.rule, period, min_period, max_period))

    @property
    def customer_id(self):
        return self.context.get('customer_id')

    @property
    def period(self):
        return self.context.get('period')


class ResponsePrice(object):
    def __init__(self, price):
        if price is None:
            raise PriceProcessingError('Price was not processed in rules.')
        try:
            str_price = '%s' % price
            Decimal(str_price)
            self.price = str_price
        except (TypeError, InvalidOperation), e:
            raise PriceProcessingError(e)
