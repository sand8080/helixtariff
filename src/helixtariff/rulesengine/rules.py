class Condition(object):
    def comply(self, req_context):
        pass

class ConcreteCond(object):
    def __init__(self, client_id):
        self.client_id = client_id

    def comply(self, req_context):
        client = getattr(req_context, 'client', None)
        if client:
            return client.id == self.client_id
        else:
            return False

class Rule(object):
    def __init__(self, cond, action):
        self.cond = cond
        self.action = action

    def comply(self, req_context):
        return self.cond.comply(req_context)

    def apply(self, price, req_context):
        return self.action.apply(price, req_context)