from datetime import datetime

class RequestContext(object):
    def __init__(self, client=None, cur_date=datetime.now()):
        self.client = client
        self.cur_date = cur_date
