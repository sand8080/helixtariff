class FalseCondition(object):
    def comply(self, req_context): #IGNORE:W0613
        return False

class BinaryOperation(object):
    def __init__(self, lh, rh):
        self.lh = lh
        self.rh = rh


class Eq(BinaryOperation):
    def __init__(self, lh, rh):
        super(Eq, self).__init__(lh, rh)

    def comply(self):
        return self.lh == self.rh


class DateEq():

#class MoreEq(Leaf):
#    """
#    lh >= rh
#    """
#    def __init__(self, lh, rh):
#        super(MoreEq, self).__init__(lh, '>=', rh)
#
#
#class LessEq(Leaf):
#    """
#    lh <= rh
#    """
#    def __init__(self, lh, rh):
#        super(LessEq, self).__init__(lh, '<=', rh)
#
#
#class Less(Leaf):
#    """
#    lh < rh
#    """
#    def __init__(self, lh, rh):
#        super(Less, self).__init__(lh, '<', rh)
#
#
#class More(Leaf):
#    """
#    lh > rh
#    """
#    def __init__(self, lh, rh):
#        super(More, self).__init__(lh, '>', rh)
#
#
#
#
#class ConcreteCond(object):
#    def __init__(self, client_id):
#        self.client_id = client_id
#
#    def comply(self, req_context):
#        client = getattr(req_context, 'client', None)
#        if client:
#            return client.id == self.client_id
#        else:
#            return False
#
#
#class NullLeaf(object):
#    """
#    Empty leaf condition
#    """
#    def glue(self):
#        return ('', [])
#
#
#class Any(object):
#    """
#    lh = ANY (rh)
#    """
#    def __init__(self, lh, rh):
#        self.lh = lh
#        self.rh = rh
#
#    def glue(self):
#        return (
#            '%%s = ANY (%s)' % self.rh,
#            [self.lh]
#        )
#
#
#class Leaf(object):
#    """
#    Leaf condition
#    """
#    def __init__(self, lh, oper, rh):
#        self.lh = lh
#        self.oper = oper
#        self.rh = rh
#
#    def glue(self):
#        return (
#            '%s %s %%s' % (buildhelpers.quote(self.lh), self.oper),
#            [self.rh]
#        )
#
#
#
#class Scoped(object):
#    def __init__(self, cond):
#        self.cond = cond
#    def glue(self):
#        cond, params = self.cond.glue()
#        return ('(%s)' % cond, params)
#
#
#class Composite(object):
#    def __init__(self, lh, oper, rh):
#        self.lh = lh
#        self.oper = oper
#        self.rh = rh
#
#    def glue(self):
#        if isinstance(self.lh, NullLeaf):
#            return self.rh.glue()
#        elif isinstance(self.rh, NullLeaf):
#            return self.lh.glue()
#        else:
#            cond_lh, params_lh = self.lh.glue()
#            cond_rh, params_rh = self.rh.glue()
#            return (
#                '%s %s %s' % (cond_lh, self.oper, cond_rh),
#                params_lh + params_rh
#            )
#
#
#class And(Composite):
#    def __init__(self, lh, rh):
#        super(And, self).__init__(lh, 'AND', rh)
#
#
#class Or(Composite):
#    def __init__(self, lh, rh):
#        super(Or, self).__init__(lh, 'OR', rh)
