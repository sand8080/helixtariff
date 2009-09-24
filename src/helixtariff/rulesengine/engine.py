from helixtariff.rulesengine.context import moc as context
from helixtariff.server.request import PriceCalculationRequest

class Engine(object):
    def process(self, request):
        '''
        Processing request as described in rule.
        Rule.
        Context used for external calls. Billing for example
        '''
        if isinstance(request, PriceCalculationRequest):
            return self._handle_price_request(request)
        else:
            raise NotImplementedError('Processor for %s not implemnted' % request.__class__)

    def get_rule(self, _):
        return 'if True: price = 3060'

    def add_line(self, to, line):
        to.append('' + line)
        print '####', to

    def create_frame(self, rule):
        frame = 'from helixtariff.rulesengine.context import moc as context\n'
        frame += 'price = 0\n'
        frame += rule
        frame += 'print price'
        return frame

    def _handle_price_request(self, request):
        expr = self.create_frame(self.get_rule(request))
        eval(expr)
#        print context.get_customer_balance(request.customer_id)
