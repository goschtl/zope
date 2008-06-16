# -*- coding: UTF-8 -*-

"""Compiles Algebra Object to python code

$Id$
"""

#BIG-BIG-BIG TODO:
# move all class.compile to here, using the adapter pattern

from zope.component import adapts
from zope.interface import implements

from ocql.interfaces import IAlgebraCompiler
from ocql.interfaces import IOptimizedAlgebraObject

from ocql.compiler.runnablequery import RunnableQuery

class AlgebraCompiler(object):
    implements(IAlgebraCompiler)
    adapts(IOptimizedAlgebraObject)

    def __init__(self, context):
        self.context = context
        #self.db = db

    def __call__(self, metadata, algebra):
        algebra = self.context
        code = algebra.compile()
        run = RunnableQuery(metadata, algebra, code)
        return run