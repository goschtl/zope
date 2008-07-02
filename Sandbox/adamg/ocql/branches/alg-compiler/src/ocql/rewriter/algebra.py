# -*- coding: UTF-8 -*-

"""Algebra operators

$Id$
"""

#
# decided to let these depend on the database
# so this is the implementation
#

from zope.interface import implements

from ocql.interfaces import IAlgebraObject
from ocql.rewriter.interfaces import *

class Algebra:
    """Signature definition of Algebra operation classes.
    shall be moved to an IF later
    """
    #TODO: this is dirty here, at the end we'll need to have a tree of
    #Algebra's whose topmost element will only get this IF
    implements(IAlgebraObject)

    def walk(self):
        """Iterate the Algebra object tree"""

class BaseAlgebra(Algebra):
    pass

class Empty(BaseAlgebra):

    implements(IEmpty)

    def __init__(self, klass, expr):
        self.klass = klass

    def __repr__(self):
        return 'Empty(%s)'%(self.klass)

    def walk(self):
        yield self

class Single(BaseAlgebra):

    implements(ISingle)

    def __init__(self, klass, expr):
        self.klass = klass
        self.expr = expr

    def __repr__(self):
        return 'Single(%s,%s)'%(self.klass, self.expr)

    def walk(self):
        yield self
        for t in self.expr.walk():
            yield t

class Union(BaseAlgebra):

    implements(IUnion)

    def __init__(self, klass, coll1, coll2):
        self.klass=klass
        self.coll1=coll1
        self.coll2=coll2

    def __repr__(self):
        return 'Union(%s,%s,%s)'%(self.klass, self.coll1, self.coll2)

    def walk(self):
        yield self
        for t in self.coll1.walk():
            yield t
        for t in self.coll2.walk():
            yield t

#class Differ:
#    def __init__(self, klass, start, end):
#        self.klass = klass
#        self.start = start
#        self.end = end
#
#    def compile(self):
#        if self.klass == set:
#            return 'set(range(%s,%s))' % (self.start.compile(),self.end.compile())
#        if self.klass == list:
#            return 'range(%s,%s)' % (self.start.compile(),self.end.compile())


class Iter(BaseAlgebra):

    implements(IIter)

    def __init__(self, klass, func, coll):
        self.klass = klass
        self.func = func
        self.coll = coll

    def __repr__(self):
        return "Iter(%s,%s,%s)"%(self.klass, self.func, self.coll)

    def walk(self):
        yield self
        for t in self.func.walk():
            yield t
        for t in self.coll.walk():
            yield t

class Select(BaseAlgebra):

    implements(ISelect)

    def __init__(self, klass, func, coll):
        self.klass = klass
        self.func = func
        self.coll = coll

    def __repr__(self):
        return "Select(%s,%s,%s)"%(self.klass, self.func, self.coll)

    def walk(self):
        yield self
        for t in self.func.walk():
            yield t
        for t in self.coll.walk():
            yield t

class Reduce(BaseAlgebra):

    implements(IReduce)

    def __init__(self, klass, expr, func, aggreg, coll):
        self.klass = klass
        self.expr = expr
        self.func = func
        self.aggreg = aggreg
        self.coll = coll

    def __repr__(self):
        return "Reduce(%s,%s,%s,%s,%s)"%(self.klass, self.expr, self.func, self.aggreg, self.coll)

    def walk(self):
        yield self
        for t in self.expr.walk():
            yield t
        for t in self.func.walk():
            yield t
        for t in self.aggreg.walk():
            yield t
        for t in self.coll.walk():
            yield t

#class Equal:
#    def __init__(self, klass, coll1, coll2):
#        self.klass = klass
#        self.coll1 = coll1
#        self.coll2 = coll2
#
#    def compile(self):
#        if self.klass == set:
#            return 'set(filter(%s,%s))' % (self.coll1.compile(),self.coll1.compile())
#        if self.klass == list:
#            return 'filter(%s,%s)' % (self.coll1.compile(),self.coll2.compile())
#
class Range(BaseAlgebra):

    implements(IRange)

    def __init__(self, klass, start, enf):
        self.klass = klass
        self.start = start
        self.end = end

    def walk(self):
        yield self
        for t in self.start.walk():
            yield t
        for t in self.end.walk():
            yield t


#class Index

class Make(BaseAlgebra):

    implements(IMake)

    def __init__(self, coll1, coll2, expr):
        self.expr = expr
        self.coll1 = coll1
        self.coll2 = coll2

    def __repr__(self):
        return "Make(%s,%s,%s)" %(self.coll1, self.coll2, self.expr)

    def walk(self):
        yield self
        for t in self.expr.walk():
            yield t

#class And:
#class Being:

class If(BaseAlgebra):

    implements(IIf)

    def __init__(self, cond, expr1, expr2):
        self.cond = cond
        self.expr1 = expr1
        self.expr2 = expr2

    def __repr__(self):
        return "If(%s,%s,%s)" % (self.cond, self.expr1, self.expr2)

    def walk(self):
        yield self
        for t in self.cond.walk():
            yield t
        for t in self.expr1.walk():
            yield t
        for t in self.expr2.walk():
            yield t

#
#
#
class Lambda(BaseAlgebra):

    implements(ILambda)

    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

    def __repr__(self):
        return "Lambda %s: %s" %(self.var, self.expr)

    def walk(self):
        yield self
        for t in self.expr.walk():
            yield t

class Constant(BaseAlgebra):

    implements(IConstant)

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "`%s`" %(self.value)

    def walk(self):
        yield self

class Identifier(BaseAlgebra):

    implements(IIdentifier)

    def __init__(self, name):
        self.name=name

    def __repr__(self):
        return "%s" % self.name

    def walk(self):
        yield self

class Binary(BaseAlgebra):

    implements(IBinary)

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return "%s%s%s" % (self.left, self.op.op, self.right)

    def walk(self):
        yield self
        for t in self.left.walk():
            yield t
        for t in self.right.walk():
            yield t

class Operator(BaseAlgebra):

    implements(IOperator)

    def __init__(self, op):
        self.op = op

    def __repr__(self):
        return self.op

    def walk(self):
        yield self

#class Property:
#   def __init__(self, left, right):
#        self.left = left
#        self.right = right
#
#    def compile(self):
#        return '%s.%s' (self.left.compile(),self.right.compile())
#
#    def __repr__(self):
#        return '%s.%s' (self.left,self.right)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
