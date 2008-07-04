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

from ocql.interfaces import IRewriter
from ocql.interfaces import IOptimizedObjectQuery
from ocql.rewriter.algebra import Algebra

from ocql.rewriter import algebra as target_algebra

class Rewriter(object):
    implements(IRewriter)
    adapts(IOptimizedObjectQuery)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        query = self.context
        alg = query.rewrite(target_algebra)        
        self._preorder(alg)
        alg.__name__ = 'head'
        return alg
    
    def _preorder(self, alg):
        if isinstance(alg, Algebra):
            for child in alg.children:
                if isinstance(child, Algebra):
                    self._preorder(child.children)
                    name = child.__name__
