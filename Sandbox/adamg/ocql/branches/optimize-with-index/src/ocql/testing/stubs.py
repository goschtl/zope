# -*- coding: UTF-8 -*-

"""component stubs for testing

$Id$
"""

from zope.component import adapts
from zope.component import provideAdapter
from zope.interface import implements

from ocql.interfaces import IQueryParser
from ocql.interfaces import IQueryOptimizer
from ocql.interfaces import IRewriter
from ocql.interfaces import IAlgebraOptimizer
from ocql.interfaces import IAlgebraCompiler
from ocql.interfaces import IDB

from ocql.interfaces import IObjectQuery
from ocql.interfaces import IOptimizedObjectQuery
from ocql.interfaces import IAlgebraObject
from ocql.interfaces import IOptimizedAlgebraObject
from ocql.interfaces import IRunnableQuery

class ObjectQueryTree(object):
    implements(IObjectQuery)

class ObjectQueryTreeOptimized(object):
    implements(IOptimizedObjectQuery)

class Algebra(object):
    implements(IAlgebraObject)

class AlgebraOptimized(object):
    implements(IOptimizedAlgebraObject)

class RunnableQuery(object):
    implements(IRunnableQuery)

class QueryParser(object):
    implements(IQueryParser)
    adapts(basestring)

    def __init__(self, context):
        self.context = context
        #self.db = db

    def __call__(self, metadata):
        strg = self.context
        return ObjectQueryTree()

class QueryOptimizer(object):
    implements(IQueryOptimizer)
    adapts(IObjectQuery)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return ObjectQueryTreeOptimized()

class Rewriter(object):
    implements(IRewriter)
    adapts(IOptimizedObjectQuery)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return Algebra()

class AlgebraOptimizer(object):
    implements(IAlgebraOptimizer)
    adapts(IAlgebraObject)

    def __init__(self, context):
        self.context = context
        #self.db = db

    def __call__(self, metadata):
        return AlgebraOptimized()

class AlgebraCompiler(object):
    implements(IAlgebraCompiler)
    adapts(IOptimizedAlgebraObject)

    def __init__(self, context):
        self.context = context
        #self.db = db

    def __call__(self, metadata, algebra):
        return RunnableQuery()

class DB(object):
    implements(IDB)
    adapts(None)

    def __init__(self, context):
        pass

def registerStubs():
    provideAdapter(QueryParser)
    provideAdapter(QueryOptimizer)
    provideAdapter(Rewriter)
    provideAdapter(AlgebraOptimizer)
    provideAdapter(AlgebraCompiler)
    provideAdapter(DB)