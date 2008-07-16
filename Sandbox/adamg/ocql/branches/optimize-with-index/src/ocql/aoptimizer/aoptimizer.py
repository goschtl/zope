# -*- coding: UTF-8 -*-

""" Optimizing will be done later,
at the moment this is just a stub returning it's input

$Id$
"""
from zope.component import adapts
from zope.interface import implements
#from zope.security.proxy import removeSecurityProxy
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides

from ocql.interfaces import IAlgebraOptimizer

from ocql.interfaces import IAlgebraObjectHead
from ocql.interfaces import IOptimizedAlgebraObject
from ocql.rewriter.algebra import BaseAlgebra, If, Single, Make, Binary

def addMarkerIF(obj, marker):
    #obj = removeSecurityProxy(obj)
    if not marker.providedBy(obj):
        directlyProvides(obj, directlyProvidedBy(obj), marker)

#only for single filter, improve later
class Finder(object):
    def __init__(self, metadata):
        #self.algebra = algebra
        self.metadata = metadata
        self.condition = None
        self.expression = None

    def visit(self, algebra):
        if isinstance(algebra , BaseAlgebra):
            for child in algebra.children:
                if isinstance(child, If):
                    if isinstance(child.cond, Binary):
                        self.condition = child.cond.left
                if isinstance(child, Make):
                    self.expression = child.expr1
                self.visit(child)

    def hasIndex(self):
        if (self.condition and self.expression) is not None:
            return self.metadata.hasPropertyIndex(self.expression, self.condition)

class AlgebraOptimizer(object):
    implements(IAlgebraOptimizer)
    adapts(IAlgebraObjectHead)

    def __init__(self, context):
        self.context = context
        #self.db = db

    def __call__(self, metadata):
        addMarkerIF(self.context, IOptimizedAlgebraObject)
        finder = Finder(metadata)
        finder.visit(self.context.tree)
        finder.hasIndex()
        return self.context
