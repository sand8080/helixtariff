from helixtariff.error import HelixtariffError
from helixtariff.rulesengine.interaction import RequestDomainPrice, ResponseDomainPrice
from helixtariff.conf.db import transaction
from helixtariff.logic import selector
from helixtariff.rulesengine.context import moc as context #IGNORE:W0611 @UnusedImport


class EngineError(HelixtariffError):
    pass


class Engine(object):
    def __init__(self):
        self.handlers = {
            RequestDomainPrice: self.on_request_domain_price,
        }

    def process(self, request):
        cls = request.__class__
        if cls not in self.handlers:
            raise EngineError('''Request of type %s can't be handled''' % cls.__name__)
        handler = self.handlers[cls]
        return handler(request)

    def on_request_domain_price(self, request):
        rule = self.load_rule(request)
        price = None

        exec rule

        response = ResponseDomainPrice(price)
        response.check_valid()
        return response

    @transaction()
    def load_rule(self, request, curs=None):
        obj = selector.get_rule(curs, request.client_id, request.tariff_name, request.service_type_name)
        return obj.rule
