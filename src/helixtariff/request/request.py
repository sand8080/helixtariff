class PriceCalculationRequest(object):
    def __init__(self, client_id, tariff_name, service_name, customer_id):
        self.client_id = client_id
        self.tariff_name = tariff_name
        self.service_name = service_name
        self.customer_id = customer_id
