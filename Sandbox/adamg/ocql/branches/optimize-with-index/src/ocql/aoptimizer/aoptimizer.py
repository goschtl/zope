# -*- coding: UTF-8 -*-

""" Optimizing will be done later,
at the moment this is just a stub returning it's input

$Id$
"""
from collections import deque
from zope.component import adapts
from zope.interface import implements
#from zope.security.proxy import removeSecurityProxy
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides

from ocql.interfaces import IAlgebraOptimizer

from ocql.interfaces import IAlgebraObjectHead
from ocql.interfaces import IOptimizedAlgebraObject
from ocql.rewriter.algebra import BaseAlgebra, If, Single, Make, Binary, Iter, Lambda

class FindResults(object):
    def __init__(self):
        self.level = 0
        self.parent = dict()

def find(tree, algebra, startlevel=0):
    results = FindResults()
    bfs_list = deque()
    bfs_list.append(tree.tree)
    results.parent[algebra] = None
    results.level = 0
    
    while len(bfs_list):
        v = bfs_list.popleft()
        if isinstance(v, algebra) and startlevel < results.level:
            return results

        for child in v.children:
            if child not in results.parent:
                results.parent[str(child.__class__)] = v
                results.level += 1
                bfs_list.append(child)
    return None

def findItrPattern(tree, algebra):
#this has If and Make algebra objects
    itr_reslts = find(tree, algebra)
    if itr_reslts is not None:
        #find for If and Make
        for child in itr_reslts.parent.values():
            if isinstance(child, Iter): 
                r_iter = child
                break

        boolean_if = boolean_make = False
        print r_iter
        for i in r_iter.children:
            if isinstance(i, Lambda):
                boolean_lambda = True
            if isinstance(i, Make):
                boolean_make = True
                
        if boolean_lambda and boolean_make:
            return r_iter

    return  None

def addMarkerIF(obj, marker):
    #obj = removeSecurityProxy(obj)
    if not marker.providedBy(obj):
        directlyProvides(obj, directlyProvidedBy(obj), marker)

class AlgebraOptimizer(object):
    implements(IAlgebraOptimizer)
    adapts(IAlgebraObjectHead)

    def __init__(self, context):
        self.context = context
        #self.db = db

    def __call__(self, metadata):
        addMarkerIF(self.context, IOptimizedAlgebraObject)
        results = findItrPattern(self.context, Iter)
        if results is not None:
            print results
        return self.context
