# -*- coding: UTF-8 -*-

"""Rewrites the Query Object to Algebra Object

$Id$
"""

#BIG-BIG-BIG TODO:
# move all queryobject.rewrite to this package
# using adapters to do the rewrite

from zope.component import adapts
from zope.interface import implements
from zope.location import locate
from zope.component import provideAdapter
from ocql.interfaces import IRewriter
from ocql.interfaces import IOptimizedObjectQuery
from ocql.rewriter.algebra import Head
from ocql.queryobject.interfaces import *

from ocql.rewriter import algebra as target_algebra

class Rewriter(object):
    implements(IRewriter)
    adapts(IOptimizedObjectQuery)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        query = self.context.tree
#        import pydevd;pydevd.settrace()
        adapter = IRewriter(query)
        alg = adapter()
        #alg = query.rewrite(target_algebra)
        head = Head(alg)
        return head


class ChildRewriter(object):
    def __init__(self, context):
        self.context = context


class IdentifierRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IIdentifier)

    def __call__(self):
        return IRewriter(self.context.name)()
        

class ConstantRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IConstant)

    def __call__(self):
        return IRewriter(self.context.value)()


class QueryRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IQuery)

    def __call__(self):
        return IRewriter(
            self.context.symbols.addlevel()
            )

class BinaryRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IBinary)

    def __call__(self):
        return IRewriter(self.context.)

class UnionRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IUnion)


class DifferRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IDiffer)


class PropertyRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IProperty)


class NotRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(INot)


class CountRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(ICount)


class QuentedRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IQuanted)


class EveryRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IEvery)


class SomeRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(ISome)


class Condition(ChildRewriter):
    implements(IRewriter)
    adapts(ICondition)


def registerAdapters():
    provideAdapter(IdentifierRewriter)
    provideAdapter(ConstantRewriter)
    provideAdapter(QueryRewriter)
    provideAdapter(BinaryRewriter)
    provideAdapter(UnionRewriter)
    provideAdapter(DifferRewriter)
    provideAdapter(PropertyRewriter)
    provideAdapter(NotRewriter)
    provideAdapter(CountRewriter)
    provideAdapter(QuentedRewriter)
    provideAdapter(EveryRewriter)
    provideAdapter(SomeRewriter)
    provideAdapter(ConstantRewriter)