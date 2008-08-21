# -*- coding: UTF-8 -*-

""" Algebra optimizer

$Id$
"""

from zope.component import adapts
from zope.interface import implements
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
    while iter_obj:
        #need to check If and Make objects present
        if (isinstance(iter_obj.func, Lambda) and isinstance(iter_obj.coll, Make)):
            if isinstance(iter_obj.func.expr, If):
                if isinstance(iter_obj.func.expr.cond , Binary):
                    return iter_obj
                else:
                    iter_obj = bfsFind(iter_obj.func)
            else:
                return None
    return None


def iterPatternMatcher(metadata, tree):
    """Replaces the identified Iter tree pattern """
    coll = tree.klass
    single = tree.func.expr.expr1
    var = tree.func.var
    interface = tree.coll.expr.name
    cond = tree.func.expr.cond.left.name
    operator = tree.func.expr.cond.op.op
    if isinstance(tree.func.expr.cond.right, Constant):
        value = tree.func.expr.cond.right.value
    elif isinstance(tree.func.expr.cond.right, Identifier):
        value = tree.func.expr.cond.right.name

    if not metadata.hasPropertyIndex(interface, cond.split(".")[1]):
        return tree.__parent__

    #new algebra objects
    makeFromIndex = MakeFromIndex(coll , coll, interface,
                                  cond.split(".")[1],
                                  operator, value=value)

    newlambda = Lambda(var, single)
    newTree = Iter(coll, newlambda, makeFromIndex)
    parent = tree.__parent__
    if isinstance(parent, Head):
        return Head(newTree)
    else:
        #possibly another optimization point, down in the algebra tree
        return None


def addMarkerIF(obj, marker):
    #obj = removeSecurityProxy(obj)
    if not marker.providedBy(obj):
        directlyProvides(obj, directlyProvidedBy(obj), marker)

class AlgebraOptimizer(object):
    implements(IAlgebraOptimizer)
    adapts(IAlgebraObjectHead)

    def __init__(self, context):
        self.context = context

    def __call__(self, metadata):
        results = findItrTreePattern(self.context.tree)

        if results is not None:
            alg = iterPatternMatcher(metadata, results)
            if alg is None:
                alg = self.context
            addMarkerIF(alg, IOptimizedAlgebraObject)
            return alg

        addMarkerIF(self.context, IOptimizedAlgebraObject)
        return self.context
