from helixtariff.error import HelixtariffError
from helixtariff.rulesengine.interaction import RequestPrice, ResponsePrice


class EngineError(HelixtariffError):
    pass


class Engine(object):
    def __init__(self):
        self.handlers = {
            RequestPrice: self.on_price_request,
        }

    def process(self, request):
        cls = request.__class__
        if cls not in self.handlers:
            raise EngineError('''Request of type %s can't be handled''' % cls.__name__)
        handler = self.handlers[cls]
        return handler(request)

    def on_price_request(self, request):
        from helixtariff.rulesengine.context import moc as context
        rule = self.load_rule(request)
        price = None

        exec rule

        response = ResponsePrice(price)
        response.check_valid()
        return response


    def load_rule(self, request):
        return ''