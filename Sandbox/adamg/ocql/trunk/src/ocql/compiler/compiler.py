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
#from ocql.interfaces import IAlgebraCompiler
from ocql.interfaces import IOptimizedAlgebraObject
#from ocql.interfaces import ICompiledAlgebraObject
from ocql.rewriter.algebra import Head

from ocql.rewriter.interfaces import *

from ocql.compiler.runnablequery import RunnableQuery

class AlgebraCompiler(object):
    implements(IAlgebraCompiler)
    adapts(IOptimizedAlgebraObject)

    def __init__(self, context):
        self.context = context
        #self.db = db

    def __call__(self, metadata, algebra):
        algebra = self.context.tree
        #code = algebra.compile()
        adapter = IAlgebraCompiler(algebra)
        code = adapter()
        run = RunnableQuery(metadata, self.context, code)
        return run

class BaseCompiler(object):
    def __init__(self, context):
        #context becomes the adapted object
        self.context = context

class EmptyCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IEmpty)

    def __call__(self):
        if self.context.klass == set:
            return 'set()'
        elif self.context.klass == list:
            return '[]'

class SingleCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(ISingle)

    def __call__(self):
        if self.context.klass == set:
            return 'set(['+IAlgebraCompiler(self.context.expr)()+'])'
        elif self.context.klass == list:
            return '['+IAlgebraCompiler(self.context.expr)()+']'

class UnionCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IUnion)

    def __call__(self):
        if self.context.klass == set:
            return 'set.union(%s, %s)' % (
                IAlgebraCompiler(self.context.coll1)(),
                IAlgebraCompiler(self.context.coll2)())
        elif self.context.klass == list:
            return '(%s)+(%s)' % (
                IAlgebraCompiler(self.context.coll1)(),
                IAlgebraCompiler(self.context.coll2)())

class DifferCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IDiffer)

    def __call__(self):
        if self.context.klass == set:
            return 'set.differ(%s, %s)' % (
                IAlgebraCompiler(self.context.coll1)(),
                IAlgebraCompiler(self.context.coll2)())

        elif self.context.klass == list:
            return '(%s)-(%s)' % (
                IAlgebraCompiler(self.context.coll1)(),
                IAlgebraCompiler(self.context.coll2)())

class IterCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IIter)

    def __call__(self):
        if self.context.func is LambdaCompiler and \
        self.context.call is set and \
        self.context.expr is IfCompiler:

            if self.context.klass == set:
                return 'reduce(set.union, map(%s, %s), set())' % (
                    IAlgebraCompiler(self.context.func)(),
                    IAlgebraCompiler(self.context.coll)())
            if self.context.klass == list:
                return 'reduce(operator.add, map(%s, %s), [])' % (
                    IAlgebraCompiler(self.context.func)(),
                    IAlgebraCompiler(self.context.coll)())
        else:
            if self.context.klass == set:
                return 'reduce(set.union, map(%s, %s), set())' % (
                    IAlgebraCompiler(self.context.func)(),
                    IAlgebraCompiler(self.context.coll)())
            if self.context.klass == list:
                return 'reduce(operator.add, map(%s, %s), [])' % (
                    IAlgebraCompiler(self.context.func)(),
                    IAlgebraCompiler(self.context.coll)())


class SelectCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(ISelect)

    def __call__(self):
        if self.context.klass == set:
            return 'set(filter(%s, %s))' % (
                IAlgebraCompiler(self.context.func)(),
                IAlgebraCompiler(self.context.call)())
        if self.context.klass == list:
            return 'filter()%s, %s' % (
                IAlgebraCompiler(self.context.func)(),
                IAlgebraCompiler(self.context.call)())


class ReduceCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IReduce)

    def __call__(self):
        if self.context.klass == set:
            return 'reduce(%s, map(%s, %s), %s)' % (
                IAlgebraCompiler(self.context.aggreg)(),
                IAlgebraCompiler(self.context.func)(),
                IAlgebraCompiler(self.context.coll)(),
                IAlgebraCompiler(self.context.expr)())
        elif self.context.klass == list:
            return 'reduce(%s, map(%s, %s), %s)'% (
                IAlgebraCompiler(self.context.aggreg)(),
                IAlgebraCompiler(self.context.func)(),
                IAlgebraCompiler(self.context.coll)(),
                IAlgebraCompiler(self.context.expr)())


class RangeCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IRange)

    def __call__(self):
        if self.context.klass == set:
            return 'set(range(%s,%s))' % (
                IAlgebraCompiler(self.context.start)(),
                IAlgebraCompiler(self.context.end)())
        elif self.context.klass == list:
            return 'range(%s,%s)' % (
                IAlgebraCompiler(self.context.start)(),
                IAlgebraCompiler(self.context.end)())


class MakeCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IMake)

    def __call__(self):
        return '%s(metadata.getAll("%s"))' % (
            self.context.coll1.__name__,
            IAlgebraCompiler(self.context.expr)())


class MakeFromIndexCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IMakeFromIndex)

    def __call__(self):
        return '%s(metadata.getFromIndex("%s", "%s", "%s", %s))' % (
            self.context.coll1.__name__,
            self.context.expr1,
            self.context.expr2,
            self.context.operator,
            self.context.value)


class IfCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IIf)

    def __call__(self):
        return '((%s) and (%s) or (%s))' % (
            IAlgebraCompiler(self.context.cond)(),
            IAlgebraCompiler(self.context.expr1)(),
            IAlgebraCompiler(self.context.expr2)())


class LambdaCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(ILambda)

    def __call__(self):
        return 'lambda %s: %s' % (
            self.context.var,
            IAlgebraCompiler(self.context.expr)())


class ConstantCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IConstant)

    def __call__(self):
        return '%s'% (self.context.value)


class IdentifierCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IIdentifier)

    def __call__(self):
        return self.context.name


class BinaryCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IBinary)

    def __call__(self):
        return '%s%s%s' % (
            IAlgebraCompiler(self.context.left)(),
            self.context.op.op,
            IAlgebraCompiler(self.context.right)())


class OperatorCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
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
    provideAdapter(DifferCompiler)
    provideAdapter(IterCompiler)
    provideAdapter(SelectCompiler)
    provideAdapter(ReduceCompiler)
    provideAdapter(RangeCompiler)
    provideAdapter(MakeCompiler)
    provideAdapter(MakeFromIndexCompiler)
    provideAdapter(IfCompiler)
    provideAdapter(LambdaCompiler)
    provideAdapter(ConstantCompiler)
    provideAdapter(IdentifierCompiler)
    provideAdapter(BinaryCompiler)
    provideAdapter(OperatorCompiler)
