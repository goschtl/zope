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
from ocql.interfaces import IOptimizedAlgebraObject
from ocql.interfaces import ICompiledAlgebraObject

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
        code = IAlgebraCompiler(self.context)()
        run = RunnableQuery(metadata, algebra, code)
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
    def __call__(self):
        if self.context.klass == set:
            return 'set(['+IAlgebraCompiler(self.context.expr)()+'])'
        elif self.context.klass == list:
            return '['+IAlgebraCompiler(self.context.expr)()+']'

def registerAdapters():
    provideAdapter(EmptyCompiler)
    provideAdapter(SingleCompiler)