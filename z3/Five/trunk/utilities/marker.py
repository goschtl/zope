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

def dottedToInterfaces(obj, seq):
    return [getInterface(obj, dotted) for dotted in seq]

def interfaceStringCheck(f):
    def wrapper(ob, interface):
        if isinstance(interface, str):
            interface = getInterface(ob, interface)
        return f(ob, interface)
    return wrapper

def mark(ob, interface):
    directlyProvides(ob, directlyProvidedBy(ob), interface)
    
def erase(ob, interface):
    directlyProvides(ob, directlyProvidedBy(ob)-interface)

mark = interfaceStringCheck(mark)
erase = interfaceStringCheck(erase)

class MarkerUtility(object):

    implements(IMarkerUtility)

    mark = staticmethod(mark)
    erase = staticmethod(erase)
    dottedToInterfaces=staticmethod(dottedToInterfaces)
    
    def getDirectlyProvided(self, obj):
        return IIntrospector(obj).getDirectlyProvided()

    def getDirectlyProvidedNames(self, obj):
        return IIntrospector(obj).getDirectlyProvidedNames()

    def getAvailableInterfaces(self, obj):
        return IIntrospector(obj).getMarkerInterfaces()

    def getAvailableInterfaceNames(self, obj):
        return IIntrospector(obj).getMarkerInterfaceNames()

    def getProvided(self, obj):
        return providedBy(obj)

    def getProvidedNames(self, obj):
        provided = providedBy(obj)
        return IIntrospector(obj).getInterfaceNames(interfaces=provided)

    def update(self, obj, add=[], remove=[]):
        """
        Currently update adds and then removes, rendering duplicate null
        """
        marker_ifaces = self.getAvailableInterfaces(obj)
        if len(add):
            [add ]
            add = Set(marker_ifaces) & Set(add)
            [mark(obj, interface) for interface in add]

        direct_ifaces = self.getDirectlyProvided(obj)
        if len(remove):
            [erase(obj, interface) for interface in Set(direct_ifaces) & Set(remove)]

_utility = MarkerUtility()
def getMarkerUtility():
    return _utility
