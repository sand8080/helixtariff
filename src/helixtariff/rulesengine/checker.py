from tokenize import generate_tokens, NAME
from StringIO import StringIO

from helixtariff.error import HelixtariffError

class RuleError(HelixtariffError):
    pass

class RuleChecker(object):
    def __init__(self, source):
        self.source = source
        self.accepted_names = set([
            'datetime',
            'now',
            'year',
            'month',
            'day',
            'if'
            'price',
            'context',
            'customer_id',
            'request',
            'response',
            'get_balance',
        ])

    def check(self):
        g = generate_tokens(StringIO(self.source).readline)   # tokenize the string
        for toknum, tokval, tok_begin, _, line  in g:
            if toknum == NAME and tokval not in self.accepted_names:
                raise RuleError('Illegal name %s at line %s: %s' % (tokval, tok_begin[0], line))


