class Tariff(object):
    def __init__(self, rules):
        self.rules = rules

    def calculate(self, request):
        price = 0
        context = request.get_context()
        for rule in self.rules:
            if rule.comply(context):
                price = rule.apply(price, context)
        return price
