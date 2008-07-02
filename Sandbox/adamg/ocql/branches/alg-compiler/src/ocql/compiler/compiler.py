# -*- coding: UTF-8 -*-

"""Compiles Algebra Object to python code

$Id$
"""

#BIG-BIG-BIG TODO:
# move all class.compile to here, using the adapter pattern

from zope.component import adapts
from zope.interface import implements
from zope.component import provideAdapter

from ocql.interfaces import IAlgebraCompiler
from ocql.interfaces import IAlgebraPartCompiler
from ocql.interfaces import IOptimizedAlgebraObject
#from ocql.interfaces import ICompiledAlgebraObject

from ocql.rewriter.interfaces import *

from ocql.compiler.runnablequery import RunnableQuery

class AlgebraCompiler(object):
    implements(IAlgebraCompiler)
    adapts(IOptimizedAlgebraObject)

    def __init__(self, context):
        self.context = context
        #self.db = db

    def __call__(self, metadata, algebra):
        algebra = self.context
        #code = algebra.compile()
        adapter = IAlgebraPartCompiler(self.context)
        code = adapter()
        run = RunnableQuery(metadata, algebra, code)
        return run

class BaseCompiler(object):
    def __init__(self, context):
        #context becomes the adapted object
        self.context = context

class EmptyCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(IEmpty)

    def __call__(self):
        if self.context.klass == set:
            return 'set()'
        elif self.context.klass == list:
            return '[]'

class SingleCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(ISingle)

    def __call__(self):
        if self.context.klass == set:
            return 'set(['+IAlgebraPartCompiler(self.context.expr)()+'])'
        elif self.context.klass == list:
            return '['+IAlgebraPartCompiler(self.context.expr)()+']'

class UnionCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(IUnion)

    def __call__(self):
        if self.context.klass == set:
            return 'set.union(%s, %s)' % (
                IAlgebraPartCompiler(self.context.coll1)(),
                IAlgebraPartCompiler(self.context.coll2)())
        elif self.context.klass == list:
            return '(%s)+(%s)' % (
                IAlgebraPartCompiler(self.context.coll1)(),
                IAlgebraPartCompiler(self.context.coll2)())

class IterCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(IIter)

    def __call__(self):
        if self.context.func is LambdaCompiler and \
        self.context.call is set and \
        self.context.expr is IfCompiler:

            if self.context.klass == set:
                return 'reduce(set.union, map(%s,%s), set())' % (
                    IAlgebraPartCompiler(self.context.func)(),
                    IAlgebraPartCompiler(self.context.coll)())
            if self.context.klass == list:
                return 'reduce(operator.add, map(%s, %s), [])' % (
                    IAlgebraPartCompiler(self.context.func)(),
                    IAlgebraPartCompiler(self.context.coll)())
        else:
            if self.context.klass == set:
                return 'reduce(set.union, map(%s,%s), set())' % (
                    IAlgebraPartCompiler(self.context.func)(),
                    IAlgebraPartCompiler(self.context.coll)())
            if self.context.klass == list:
                return 'reduce(operator.add, map(%s, %s), [])' % (
                    IAlgebraPartCompiler(self.context.func)(),
                    IAlgebraPartCompiler(self.context.coll)())


class SelectCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(ISelect)

    def __call__(self):
        if self.context.klass == set:
            return 'set(filter(%s, %s))' % (
                IAlgebraPartCompiler(self.context.func)(),
                IAlgebraPartCompiler(self.context.call)())
        if self.context.klass == list:
            return 'filter()%s, %s' % (
                IAlgebraPartCompiler(self.context.func)(),
                IAlgebraPartCompiler(self.context.call)())


class ReduceCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(IReduce)

    def __call__(self):
        if self.context.klass == set:
            return 'reduce(%s, map(%s, %s), %s)' % (
                IAlgebraPartCompiler(self.context.aggreg)(),
                IAlgebraPartCompiler(self.context.func)(),
                IAlgebraPartCompiler(self.context.coll)(),
                IAlgebraPartCompiler(self.context.expr)())
        elif self.context.klass == list:
            return 'reduce(%s, map(%s, %s), %s)'% (
                IAlgebraPartCompiler(self.context.aggreg)(),
                IAlgebraPartCompiler(self.context.func)(),
                IAlgebraPartCompiler(self.context.coll)(),
                IAlgebraPartCompiler(self.context.expr)())


class RangeCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(IRange)

    def __call__(self):
        if self.context.klass == set:
            return 'set(range(%s,%s))' % (
                IAlgebraPartCompiler(self.context.start)(),
                IAlgebraPartCompiler(self.context.end)())
        elif self.context.klass == list:
            return 'range(%s,%s)' % (
                IAlgebraPartCompiler(self.context.start)(),
                IAlgebraPartCompiler(self.context.end)())


class MakeCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(IMake)

    def __call__(self):
        return '%s(metadata.getAll("%s"))' % (
            self.context.coll1.__name__,
            IAlgebraPartCompiler(self.context.expr)())


class IfCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(IIf)

    def __call__(self):
        return '((%s) and (%s) or (%s))' % (
            IAlgebraPartCompiler(self.context.cond)(),
            IAlgebraPartCompiler(self.context.expr1)(),
            IAlgebraPartCompiler(self.context.expr2)())


class LambdaCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(ILambda)

    def __call__(self):
        return 'lambda %s: %s'%(
            self.context.var,
            IAlgebraPartCompiler(self.context.expr)())


class ConstantCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(IConstant)

    def __call__(self):
        return '%s'% (self.context.value)


class IdentifierCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(IIdentifier)

    def __call__(self):
        return self.context.name


class BinaryCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(IBinary)

    def __call__(self):
        return '%s%s%s' % (
            IAlgebraPartCompiler(self.context.left)(),
            self.context.op.op,
            IAlgebraPartCompiler(self.context.right)())


class OperatorCompiler(BaseCompiler):
    implements(IAlgebraPartCompiler)
    adapts(IOperator)

    ops = {
        'or': 'operator.or_',
        'and': 'operator.and_',
        'not': 'operator.not_',
        '+': 'operator.add', '-': 'operator.sub',
        '*': 'operator.mul', '/': 'operator.div',
        '<': 'operator.lt', '>': 'operator.gt',
        '<=': 'operator.le', '>=': 'operator.ge',
        '==': 'operator.eq', '~=': 'operator.ne',
        }

    def __call__(self):
        return self.ops[self.context.op]


def registerAdapters():
    provideAdapter(EmptyCompiler)
    provideAdapter(SingleCompiler)
    provideAdapter(UnionCompiler)
    provideAdapter(IterCompiler)
    provideAdapter(SelectCompiler)
    provideAdapter(ReduceCompiler)
    provideAdapter(RangeCompiler)
    provideAdapter(MakeCompiler)
    provideAdapter(IfCompiler)
    provideAdapter(LambdaCompiler)
    provideAdapter(ConstantCompiler)
    provideAdapter(IdentifierCompiler)
    provideAdapter(BinaryCompiler)
    provideAdapter(OperatorCompiler)
