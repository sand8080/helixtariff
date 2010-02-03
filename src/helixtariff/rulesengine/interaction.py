from decimal import Decimal, InvalidOperation


class PriceProcessingError(Exception):
    pass


class RequestPrice(dict):
    def __init__(self, rule, context=None):
        ctx = {} if context is None else context
        super(RequestPrice, self).__init__(ctx)
        self.rule = rule

    def check_period(self, min_period=1, max_period=1):
        period = self.period
        if period is None or period < min_period or period > max_period:
            raise PriceProcessingError('In rule %s period %s out of bounds: [%s, %s]' %
                (self.rule, period, min_period, max_period))

    @property
    def customer_id(self):
        return self.get('customer_id', None)

    @property
    def period(self):
        return self.get('period', None)


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
