# -*- coding: UTF-8 -*-

"""Main

$Id$
"""

from zope.interface import implements
from zope.component import getAdapter

from ocql.interfaces import IEngine

from ocql.interfaces import IQueryParser
from ocql.interfaces import IQueryOptimizer
from ocql.interfaces import IRewriter
from ocql.interfaces import IAlgebraOptimizer
from ocql.interfaces import IAlgebraCompiler
from ocql.interfaces import IDB

from ocql.interfaces import IOptimizedObjectQuery
from ocql.interfaces import IAlgebraObject
from ocql.interfaces import IOptimizedAlgebraObject
from ocql.interfaces import IRunnableQuery
from ocql.interfaces import IObjectQueryHead

class OCQLEngine:
    implements(IEngine)

    def __init__(self):
        pass

    def compile(self, query):
        #TODO: later use maybe named adapters
        metadata = IDB(None)
        if IObjectQueryHead.providedBy(query):
            objectquery = query
        else:
            objectquery = IQueryParser(query)(metadata)

        optimizedoq = IQueryOptimizer(objectquery)()
        algebra = IRewriter(optimizedoq)()
        optimizedalgebra = IAlgebraOptimizer(algebra)(metadata)
        #algebra is passed here to keep track of the original one, not the optimized
        runnable = IAlgebraCompiler(optimizedalgebra)(metadata, algebra)

        return runnable
