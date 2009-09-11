class Rule(object):
    def __init__(self, cond, action):
        self.cond = cond
        self.action = action

    def comply(self, req_context):
        return self.cond.comply(req_context)

    def apply(self, price, req_context):
        return self.action.apply(price, req_context)