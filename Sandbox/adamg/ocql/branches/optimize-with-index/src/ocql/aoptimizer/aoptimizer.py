# -*- coding: UTF-8 -*-

""" Optimizing will be done later,
at the moment this is just a stub returning it's input

$Id$
"""
from collections import deque
from zope.component import adapts
from zope.interface import implements
from zope.location import locate
#from zope.security.proxy import removeSecurityProxy
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides

from ocql.interfaces import IAlgebraOptimizer

from ocql.interfaces import IAlgebraObjectHead
from ocql.interfaces import IOptimizedAlgebraObject
from ocql.rewriter.algebra import *

def bfsFind(tree):
    """Breadth-first search to find a Iter Algebra object."""
    visited = set()
    queue = [tree]
    while len(queue):
        curr_node = queue.pop(0)
        if isinstance(curr_node, Iter):
            return curr_node
        if isinstance(curr_node, BaseAlgebra):
            visited.add(curr_node)
            queue.extend(c for c in curr_node.children
                         if c not in visited and c not in queue)


def findItrTreePattern(tree):
    """Checks whole Iter tree pattern exists stating from the Iter algebra object"""
    iter_obj = bfsFind(tree)
    if iter_obj is not None:
        #need to check If and Make objects present
        if (isinstance(iter_obj.func, Lambda) and isinstance(iter_obj.coll, Make)):
            if isinstance(iter_obj.func.expr, If):
                if isinstance(iter_obj.func.expr.cond , Binary):
                    return iter_obj
    return None


def iterPatternMatcher(tree):
    """Replaces the identified Iter tree pattern """
    coll = tree.klass
    single = tree.func.expr.expr1
    var = tree.func.var
    interface = tree.coll.expr1.name
    cond = tree.func.expr.cond.left.name
    operator = tree.func.expr.cond.op.op
    if isinstance(tree.func.expr.cond.right, Constant):
        value = tree.func.expr.cond.right.value
    elif isinstance(tree.func.expr.cond.right, Identifier):
        value = tree.func.expr.cond.right.name
    else:
        return tree
    #new algebra objects
    if operator == '==':
        makeFromIndex = MakeFromIndex(coll , coll, interface,
                                      cond.split(".")[1],
                                      lowerbound=value, upperbound=value)
    elif operator == '>' or operator == '>=':
        makeFromIndex = MakeFromIndex(coll , coll, interface,
                                      cond.split(".")[1],
                                      lowerbound=value, upperbound=None)
    elif operator == '<' or operator == '<=':
        makeFromIndex = MakeFromIndex(coll , coll, interface,
                                      cond.split(".")[1],
                                      lowerbound=None, upperbound=value)
    else:
        return tree

    newlambda = Lambda(var, single)
    newTree = Iter(coll, newlambda, makeFromIndex)
    parent = tree.__parent__
    if isinstance(parent, Head):
        return Head(newTree)
    else:
        for c in parent.children:
            if isinstance(c, Iter):
                del c
        parent.children.append(newTree)
        locate(newTree, parent, 'iter')
        return newTree


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
        results = findItrTreePattern(self.context.tree)

        if results is not None:
            alg = iterPatternMatcher(results)
            addMarkerIF(alg, IOptimizedAlgebraObject)
            return alg

        addMarkerIF(self.context, IOptimizedAlgebraObject)
        return self.context
