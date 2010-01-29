from tokenize import generate_tokens, NAME, OP
from StringIO import StringIO

from helixtariff.error import HelixtariffError
from helixtariff.rulesengine.interaction import PriceProcessingError


class RuleError(HelixtariffError):
    pass


class RuleChecker(object):
    def __init__(self):
        self.accepted_names = set([
            'datetime', 'now', 'year', 'month', 'day',
            'if', 'else', 'and', 'not', 'in', 'None', 'for',
            'response', 'price',
            'context', 'get_balance',
            'request', 'customer_id', 'period', 'check_period', 'min_period', 'max_period',
        ])
        self.accepted_ops = set([
            '=', '+=', '-=',
            '+', '-', '*', '/', '%',
            '==', '>', '<', '<=', '>=', '!=', '<>',
            '(', ')', '[', ']', '.', ',', ':',
        ])
        self.required_names = set(['price'])

    def check(self, source):
        g = generate_tokens(StringIO(source).readline)
        req_names = set(self.required_names)
        for toknum, tokval, tok_begin, _, line  in g:
            if toknum == NAME and tokval not in self.accepted_names:
                raise RuleError("Illegal name '%s' at line %s: %s" % (tokval, tok_begin[0], line))
            if toknum == NAME and tokval in req_names:
                req_names.remove(tokval)
            if toknum == OP and tokval not in self.accepted_ops:
                raise RuleError("Illegal operator '%s' at line %s: %s" % (tokval, tok_begin[0], line))
        if req_names:
            raise PriceProcessingError("Required values not processed: '%s'" % req_names)