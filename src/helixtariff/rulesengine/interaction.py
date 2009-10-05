from decimal import Decimal, Context, DecimalException

class PriceProcessingError(Exception):
    pass


class RequestDomainPrice(object):
    def __init__(self, client_id, tariff_name, service_type_name, period=1, customer_id=None):
        self.client_id = client_id
        self.tariff_name = tariff_name
        self.service_type_name = service_type_name
        self.period = period
        self.customer_id = customer_id

    def check_period(self, min_period=1, max_period=1):
        if self.period < min_period or self.period > max_period:
            raise PriceProcessingError('Service %s period %s out of bounds: [%s, %s]' %
                (self.service_type_name, self.period, min_period, max_period))


class ResponseDomainPrice(object):
    def __init__(self, price):
        try:
            self.price = Decimal('%s' % price, Context(prec=2))
        except DecimalException:
            raise PriceProcessingError('Invalid price value: %s.' % price)

    def check_valid(self):
        if self.price is None:
            raise PriceProcessingError('Domain price was not processed in rules.')