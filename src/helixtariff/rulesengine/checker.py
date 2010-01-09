from tokenize import generate_tokens, NAME
from StringIO import StringIO

from helixtariff.error import HelixtariffError

class RuleError(HelixtariffError):
    pass

class RuleChecker(object):
    def __init__(self):
        self.accepted_names = set([
            'datetime', 'now', 'year', 'month', 'day',
            'if', 'else',
            'response', 'price',
            'context', 'get_balance',
            'request', 'customer_id', 'period', 'check_period', 'min_period', 'max_period',
        ])

    def check(self, source):
        g = generate_tokens(StringIO(source).readline)   # tokenize the string
        for toknum, tokval, tok_begin, _, line  in g:
            if toknum == NAME and tokval not in self.accepted_names:
                raise RuleError('Illegal name %s at line %s: %s' % (tokval, tok_begin[0], line))
