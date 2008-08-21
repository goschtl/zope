# -*- coding: UTF-8 -*-

"""Algebra operators

$Id$
"""

from zope.interface import implements

from ocql.interfaces import IAlgebraObject
from ocql.interfaces import IAlgebraObjectHead
from ocql.rewriter.interfaces import *
from zope.location import Location, locate
from zope.location.interfaces import ILocation

class Head(Location):
    implements(IAlgebraObjectHead)

    def __init__(self, tree):
        name = 'head'
        self.tree = tree
        locate(tree, self, 'tree')

    def walk(self):
        return self.tree.walk()

    def __repr__(self):
        return ('Head(%s)') % (self.tree)

class BaseAlgebra(Location):
    implements(IAlgebraObject)

    def __init__(self):
        self.children = []

    def setProp(self, name, value):
        setattr(self, name, value)
        if ILocation.providedBy(value):
            locate(value, self, name)
            self.children.append(value)

    def walk(self):
        yield self
        for child in self.children:
            for t in child.walk():
                yield t

class Empty(BaseAlgebra):
    implements(IEmpty)

    def __init__(self, klass):
        BaseAlgebra.__init__(self)
        self.setProp('klass', klass)

    def __repr__(self):
        return 'Empty(%s)'%(self.klass)

class Single(BaseAlgebra):
    implements(ISingle)

    def __init__(self, klass, expr):
        BaseAlgebra.__init__(self)
        self.setProp('klass', klass)
        self.setProp('expr', expr)

    def __repr__(self):
        return 'Single(%s, %s)'%(self.klass, self.expr)

class Union(BaseAlgebra):
    implements(IUnion)

    def __init__(self, klass, coll1, coll2):
        BaseAlgebra.__init__(self)
        self.setProp('klass', klass)
        self.setProp('coll1', coll1)
        self.setProp('coll2', coll2)

    def __repr__(self):
        return 'Union(%s, %s, %s)' % (self.klass, self.coll1, self.coll2)

class Differ(BaseAlgebra):
    implements(IDiffer)

    def __init__(self, klass, coll1, coll2):
        BaseAlgebra.__init__(self)
        self.setProp('klass', klass)
        self.setProp('coll1', coll1)
        self.setProp('coll2', coll2)

    def __repr__(self):
        return 'Differ(%s, %s, %s)' % (self.klass, self.coll1, self.coll2)

class Iter(BaseAlgebra):
    implements(IIter)

    def __init__(self, klass, func, coll):
        BaseAlgebra.__init__(self)
        self.setProp('klass', klass)
        self.setProp('func', func)
        self.setProp('coll', coll)

    def __repr__(self):
        return "Iter(%s, %s, %s)"%(self.klass, self.func, self.coll)

class Select(BaseAlgebra):
    implements(ISelect)

    def __init__(self, klass, func, coll):
        BaseAlgebra.__init__(self)
        self.setProp('klass', klass)
        self.setProp('func', func)
        self.setProp('coll', coll)

    def __repr__(self):
        return "Select(%s, %s, %s)"%(self.klass, self.func, self.coll)

class Reduce(BaseAlgebra):
    implements(IReduce)

    def __init__(self, klass, expr, func, aggreg, coll):
        BaseAlgebra.__init__(self)
        self.setProp('klass', klass)
        self.setProp('expr', expr)
        self.setProp('func', func)
        self.setProp('aggreg', aggreg)
        self.setProp('coll', coll)

    def __repr__(self):
        return "Reduce(%s, %s, %s, %s, %s)"%(self.klass, self.expr, self.func, self.aggreg, self.coll)

#class Equal:
#    def __init__(self, klass, coll1, coll2):
#        self.setProp('klass', klass)
#        self.setProp('coll1', coll1)
#        self.setProp('coll2', coll2)
#
#    def compile(self):
#        if self.klass == set:
#            return 'set(filter(%s, %s))' % (self.coll1.compile(),self.coll1.compile())
#        if self.klass == list:
#            return 'filter(%s, %s)' % (self.coll1.compile(),self.coll2.compile())
#
class Range(BaseAlgebra):
    implements(IRange)

    def __init__(self, klass, start, end):
        BaseAlgebra.__init__(self)
        self.setProp('klass', klass)
        self.setProp('start', start)
        self.setProp('end', end)

    def __repr__(self):
        return "Range(%s, %s, %s)" %(self.klass, self.start, self.end)

#class Index

class Make(BaseAlgebra):
    implements(IMake)

    def __init__(self, coll1, coll2, expr):
        BaseAlgebra.__init__(self)
        self.setProp('expr', expr)
        self.setProp('coll1', coll1)
        self.setProp('coll2', coll2)

    def __repr__(self):
        return "Make(%s, %s, %s)" %(self.coll1, self.coll2, self.expr)


class MakeFromIndex(BaseAlgebra):

    implements(IMakeFromIndex)

    def __init__(self, coll1, coll2, expr1, expr2, operator, value):
        BaseAlgebra.__init__(self)
        self.setProp('expr1', expr1)
        self.setProp('expr2', expr2)
        self.setProp('coll1', coll1)
        self.setProp('coll2', coll2)
        self.setProp('operator', operator)
        self.setProp('value', value)

    def __repr__(self):
        return "MakeFromIndex(%s, %s, %s, %s, %s)" % (
            self.coll1, self.coll2, self.expr1, self.expr2, self.value)


#class And:
#class Being:

class If(BaseAlgebra):
    implements(IIf)

    def __init__(self, cond, expr1, expr2):
        BaseAlgebra.__init__(self)
        self.setProp('cond', cond)
        self.setProp('expr1', expr1)
        self.setProp('expr2', expr2)

    def __repr__(self):
        return "If(%s, %s, %s)" % (self.cond, self.expr1, self.expr2)

#
#
#
class Lambda(BaseAlgebra):
    implements(ILambda)

    def __init__(self, var, expr):
        BaseAlgebra.__init__(self)
        self.setProp('var', var)
        self.setProp('expr', expr)

    def __repr__(self):
        return "Lambda %s: %s" %(self.var, self.expr)

class Constant(BaseAlgebra):
    implements(IConstant)

    def __init__(self, value):
        BaseAlgebra.__init__(self)
        self.value = value

    def __repr__(self):
        return "`%s`" %(self.value)

class Identifier(BaseAlgebra):
    implements(IIdentifier)

    def __init__(self, name):
        BaseAlgebra.__init__(self)
        self.name=name

    def __repr__(self):
        return "%s" % self.name

class Binary(BaseAlgebra):
    implements(IBinary)

    def __init__(self, left, op, right):
        BaseAlgebra.__init__(self)
        self.setProp('left', left)
        self.setProp('op', op)
        self.setProp('right', right)

    def __repr__(self):
        return "%s%s%s" % (self.left, self.op, self.right)

class Operator(BaseAlgebra):
    implements(IOperator)

    def __init__(self, op):
        BaseAlgebra.__init__(self)
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