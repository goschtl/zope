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

from ocql.interfaces import IAlgebraObject
from ocql.interfaces import IOptimizedAlgebraObject

def addMarkerIF(obj, marker):
    #obj = removeSecurityProxy(obj)
    if not marker.providedBy(obj):
        directlyProvides(obj, directlyProvidedBy(obj), marker)

class AlgebraOptimizer(object):
    implements(IAlgebraOptimizer)
    adapts(IAlgebraObject)

    def __init__(self, context):
        self.context = context
        #self.db = db

    def __call__(self):
        addMarkerIF(self.context, IOptimizedAlgebraObject)
        return self.context
