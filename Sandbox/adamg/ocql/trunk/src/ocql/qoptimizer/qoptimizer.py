# -*- coding: UTF-8 -*-

""" Query optimizer

Optimizing will be done later,
at the moment this is just a stub returning it's input

$Id$
"""

from zope.component import adapts
from zope.interface import implements
#from zope.security.proxy import removeSecurityProxy
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides

from ocql.interfaces import IQueryOptimizer

from ocql.interfaces import IObjectQueryHead
from ocql.interfaces import IOptimizedObjectQuery

def addMarkerIF(obj, marker):
    #obj = removeSecurityProxy(obj)
    if not marker.providedBy(obj):
        directlyProvides(obj, directlyProvidedBy(obj), marker)

class QueryOptimizer(object):
    implements(IQueryOptimizer)
    adapts(IObjectQueryHead)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        addMarkerIF(self.context, IOptimizedObjectQuery)
        return self.context