from decimal import Decimal, Context, DecimalException


class PriceProcessingError(Exception):
    pass


class RequestPrice(object):
    def __init__(self, rule, context=None):
        self.rule = rule
        self.context = context if context is not None else {}

    def check_period(self, min_period=1, max_period=1):
        period = self.context.get('period')
        if period is None or period < min_period or period > max_period:
            raise PriceProcessingError('In rule %s period %s out of bounds: [%s, %s]' %
                (self.rule.id, period, min_period, max_period))

    @property
    def customer_id(self):
        return self.context.get('customer_id')

    @property
    def period(self):
        return self.context.get('period')


class ResponsePrice(object):
    def __init__(self, price):
        self.price = price

    def check_valid(self):
        if self._price is None:
            raise PriceProcessingError('Price was not processed in rules.')

    def get_price(self):
        return '%s' % self._price

    def set_price(self, price):
        try:
            self._price = Decimal('%s' % price, Context(prec=2)) #IGNORE:W0201
        except DecimalException:
            raise PriceProcessingError('Invalid price value: %s.' % price)

    # Hiding price for Decimal precision processing
    price = property(get_price, set_price)
