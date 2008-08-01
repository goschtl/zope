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
from ocql.interfaces import IAlgebraObjectHead
from ocql.rewriter.interfaces import *
from zope.location import Location, locate

class Head(Location):
    implements(IAlgebraObjectHead)

    def __init__(self, tree):
        name = 'head'
        self.tree = tree
        locate(tree, self, 'tree')

    def walk(self):
        yield self.tree

    def __repr__(self):
        return ('%s') % (self.tree)

class BaseAlgebra(Location):
    implements(IAlgebraObject)
    children = []

    def walk(self):
        yield self
        for child in self.children:
            for t in child.walk():
                yield t

class Empty(BaseAlgebra):
    implements(IEmpty)

    def __init__(self, klass, expr):
        self.klass = klass

    def __repr__(self):
        return 'Empty(%s)'%(self.klass)

class Single(BaseAlgebra):
    implements(ISingle)

    def __init__(self, klass, expr):
        self.klass = klass
        self.expr = expr
        locate(expr, self, 'expr')
        self.children.extend([klass, expr])

    def __repr__(self):
        return 'Single(%s,%s)'%(self.klass, self.expr)

class Union(BaseAlgebra):
    implements(IUnion)

    def __init__(self, klass, coll1, coll2):
        self.klass=klass
        self.coll1=coll1
        self.coll2=coll2
        locate(coll1, self, 'coll1')
        locate(coll2, self, 'coll2')
        self.children.extend([coll1, coll2])

    def __repr__(self):
        return 'Union(%s,%s,%s)'%(self.klass, self.coll1, self.coll2)

class Differ:
    implements(IDiffer)

    def __init__(self, klass, start, end):
        self.klass = klass
        self.start = start
        self.end = end

    def __repr__(self):
        return 'Differ(%s,%s,%s)'%(self.klass, self.start, self.end)

class Iter(BaseAlgebra):
    implements(IIter)

    def __init__(self, klass, func, coll):
        self.klass = klass
        self.func = func
        self.coll = coll
        locate(func, self, 'func')
        locate(coll, self, 'coll')
        self.children.extend([func,coll])

    def __repr__(self):
        return "Iter(%s,%s,%s)"%(self.klass, self.func, self.coll)

class Select(BaseAlgebra):
    implements(ISelect)

    def __init__(self, klass, func, coll):
        self.klass = klass
        self.func = func
        self.coll = coll
        locate(func, self, 'func')
        locate(coll, self, 'coll')
        self.children.extend([func,coll])

    def __repr__(self):
        return "Select(%s,%s,%s)"%(self.klass, self.func, self.coll)

class Reduce(BaseAlgebra):
    implements(IReduce)

    def __init__(self, klass, expr, func, aggreg, coll):
        self.klass = klass
        self.expr = expr
        self.func = func
        self.aggreg = aggreg
        self.coll = coll
        locate(expr, self, 'expr')
        locate(func, self, 'func')
        locate(aggreg, self, 'aggreg')
        locate(coll, self, 'coll')
        self.children.extend([expr, func, aggreg, coll])

    def __repr__(self):
        return "Reduce(%s,%s,%s,%s,%s)"%(self.klass, self.expr, self.func, self.aggreg, self.coll)

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

    def __init__(self, klass, start, end):
        self.klass = klass
        self.start = start
        self.end = end
        locate(start, self, 'start')
        locate(end, self, 'end')
        self.children.extend([start, end])

#class Index

class Make(BaseAlgebra):
    implements(IMake)

    def __init__(self, coll1, coll2, expr):
        self.expr = expr
        self.coll1 = coll1
        self.coll2 = coll2
        locate(expr, self, 'expr')
#        locate(coll1, self, 'coll1')
#        locate(coll2, self, 'coll2')
        self.children.append(expr)

    def __repr__(self):
        return "Make(%s,%s,%s)" %(self.coll1, self.coll2, self.expr)


#class And:
#class Being:

class If(BaseAlgebra):
    implements(IIf)

    def __init__(self, cond, expr1, expr2):
        self.cond = cond
        self.expr1 = expr1
        self.expr2 = expr2
        locate(cond, self, 'cond')
        locate(expr1, self, 'expr1')
        locate(expr2, self, 'expr2')
        self.children.extend([cond, expr1, expr2])

    def __repr__(self):
        return "If(%s,%s,%s)" % (self.cond, self.expr1, self.expr2)

#
#
#
class Lambda(BaseAlgebra):
    implements(ILambda)

    def __init__(self, var, expr):
        self.var = var
        self.expr = expr
        locate(expr, self, 'expr')
        self.children.append(expr)

    def __repr__(self):
        return "Lambda %s: %s" %(self.var, self.expr)

class Constant(BaseAlgebra):
    implements(IConstant)

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "`%s`" %(self.value)

class Identifier(BaseAlgebra):
    implements(IIdentifier)

    def __init__(self, name):
        self.name=name

    def __repr__(self):
        return "%s" % self.name

class Binary(BaseAlgebra):
    implements(IBinary)

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        locate(left, self, 'left')
        locate(right, self, 'right')
        self.children.extend([left, right])

    def __repr__(self):
        return "%s%s%s" % (self.left, self.op.op, self.right)

class Operator(BaseAlgebra):
    implements(IOperator)

    def __init__(self, op):
        self.op = op

    def __repr__(self):
        return self.op

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
