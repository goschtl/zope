##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
MarkerUtility allows for arbitrary application of marker interfaces to objects.

$Id: $
"""
from sets import Set

from zope.interface import providedBy, implements
from zope.interface import directlyProvides, directlyProvidedBy
from zope.app.introspector.interfaces import IIntrospector
from zope.app.component.interface import getInterface
from Products.Five.utilities.interfaces import IMarkerUtility

#from zope.app.container.contained import Contained
#from persistent import Persistent

def mark(ob, interface):
    directlyProvides(ob, directlyProvidedBy(ob), interface)
    
def erase(ob, interface):
    directlyProvides(ob, directlyProvidedBy(ob)-interface)

# not sure this needs containment or persistence
# or to be local
class MarkerUtility(object):

    implements(IMarkerUtility)

    mark = staticmethod(mark)
    erase = staticmethod(erase)

    def getDirectlyProvided(self, context):
        return IIntrospector(context).getDirectlyProvided()

    def getDirectlyProvidedNames(self, context):
        return IIntrospector(context).getDirectlyProvidedNames()

    def getMarkerInterfaces(self, context):
        return IIntrospector(context).getMarkerInterfaces()

    def getMarkerInterfaceNames(self, context):
        return IIntrospector(context).getMarkerInterfaceNames()

    def getProvided(self, context):
        return providedBy(context)

    def getProvidedNames(self, context):
        provided = providedBy(context)
        return IIntrospector(context).getInterfaceNames(interfaces=provided)

    def update(self, obj, add=[], remove=[]):
        """
        Currently update adds and then removes, rendering duplicate null
        """
        marker_ifaces = self.getMarkerInterfaces(obj)
        if len(add):
            [mark(obj, interface) for interface in Set(marker_ifaces) & Set(add)]

        direct_ifaces = self.getDirectlyProvided(obj)
        if len(remove):
            [erase(obj, interface) for interface in Set(direct_ifaces) & Set(remove)]

_utility = MarkerUtility()
def getMarkerUtility():
    return _utility
