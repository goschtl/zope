# -*- coding: UTF-8 -*-

"""Compiles Algebra Object to python code

$Id$
"""

from zope.component import adapts
from zope.interface import implements
from zope.component import provideAdapter

from ocql.interfaces import IAlgebraCompiler
from ocql.interfaces import IOptimizedAlgebraObject
from ocql.rewriter.algebra import Head

from ocql.rewriter.interfaces import *

from ocql.compiler.runnablequery import RunnableQuery

RELAX_COMPILE = False

def compile(expr):
    #nasty?? thing to allow compilation of not fully compliant algebra tree
    #mostly required for demonstration purposes
    try:
        code = IAlgebraCompiler(expr)()
    except TypeError:
        if RELAX_COMPILE:
            if isinstance(expr, basestring):
                return expr
            return unicode(expr)
        else:
            raise
    return code

class AlgebraCompiler(object):
    implements(IAlgebraCompiler)
    adapts(IOptimizedAlgebraObject)

    def __init__(self, context):
        self.context = context

    def __call__(self, metadata, originalAlgebra):
        code = compile(self.context.tree)
        run = RunnableQuery(metadata, originalAlgebra, code)
        return run

class BaseCompiler(object):
    def __init__(self, context):
        #context becomes the adapted (algebra) object
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
            return 'set(['+compile(self.context.expr)+'])'
        elif self.context.klass == list:
            return '['+compile(self.context.expr)+']'

class UnionCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IUnion)

    def __call__(self):
        if self.context.klass == set:
            return 'set.union(%s, %s)' % (
                compile(self.context.coll1),
                compile(self.context.coll2))
        elif self.context.klass == list:
            return '(%s+filter(lambda x:x not in %s,%s))' % (
                compile(self.context.coll1),
                compile(self.context.coll1),
                compile(self.context.coll2))

class DifferCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IDiffer)

    def __call__(self):
        if self.context.klass == set:
            return 'set.difference(%s, %s)' % (
                compile(self.context.coll1),
                compile(self.context.coll2))

        elif self.context.klass == list:
            return '(filter(lambda x:x not in %s,%s))' % (
                compile(self.context.coll2),
                compile(self.context.coll1))

class IterCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IIter)

    def __call__(self):
        if self.context.klass == set:
            return 'reduce(set.union, map(%s, %s), set())' % (
                compile(self.context.func),
                compile(self.context.coll))
        if self.context.klass == list:
            return 'reduce(operator.add, map(%s, %s), [])' % (
                compile(self.context.func),
                compile(self.context.coll))


class SelectCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(ISelect)

    def __call__(self):
        if self.context.klass == set:
            return 'set(filter(%s, %s))' % (
                compile(self.context.func),
                compile(self.context.coll))
        if self.context.klass == list:
            return 'filter(%s, %s)' % (
                compile(self.context.func),
                compile(self.context.coll))


class ReduceCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IReduce)

    def __call__(self):
        if self.context.klass == set:
            return 'reduce(%s, map(%s, %s), %s)' % (
                compile(self.context.aggreg),
                compile(self.context.func),
                compile(self.context.coll),
                compile(self.context.expr))
        elif self.context.klass == list:
            return 'reduce(%s, map(%s, %s), %s)'% (
                compile(self.context.aggreg),
                compile(self.context.func),
                compile(self.context.coll),
                compile(self.context.expr))


class RangeCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IRange)

    def __call__(self):
        if self.context.klass == set:
            return 'set(range(%s,%s))' % (
                compile(self.context.start),
                compile(self.context.end))
        elif self.context.klass == list:
            return 'range(%s,%s)' % (
                compile(self.context.start),
                compile(self.context.end))


class MakeCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(IMake)

    def __call__(self):
        return '%s(metadata.getAll("%s"))' % (
            self.context.coll1.__name__,
            compile(self.context.expr))


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
            compile(self.context.cond),
            compile(self.context.expr1),
            compile(self.context.expr2))


class LambdaCompiler(BaseCompiler):
    implements(IAlgebraCompiler)
    adapts(ILambda)

    def __call__(self):
        return 'lambda %s: %s' % (
            self.context.var,
            compile(self.context.expr))


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
        return '%s %s %s' % (
            compile(self.context.left),
            self.context.op.op,
            compile(self.context.right))


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

#
#def registerAdapters():
#    provideAdapter(EmptyCompiler)
#    provideAdapter(SingleCompiler)
#    provideAdapter(UnionCompiler)
#    provideAdapter(DifferCompiler)
#    provideAdapter(IterCompiler)
#    provideAdapter(SelectCompiler)
#    provideAdapter(ReduceCompiler)
#    provideAdapter(RangeCompiler)
#    provideAdapter(MakeCompiler)
#    provideAdapter(MakeFromIndexCompiler)
#    provideAdapter(IfCompiler)
#    provideAdapter(LambdaCompiler)
#    provideAdapter(ConstantCompiler)
#    provideAdapter(IdentifierCompiler)
#    provideAdapter(BinaryCompiler)
#    provideAdapter(OperatorCompiler)
