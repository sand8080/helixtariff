from decimal import Decimal, Context, DecimalException

class PriceProcessingError(Exception):
    pass


class RequestPrice(object):
    pass


class ResponsePrice(object):
    def __init__(self, price):
        try:
            self.price = Decimal('%s' % price, Context(prec=2))
        except DecimalException:
            raise PriceProcessingError('Invalid price value: %s.' % price)

    def check_valid(self):
        if self.price is None:
            raise PriceProcessingError('Price was not processed in rules.')