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

$Id$
"""
from sets import Set

from zope.interface import implements
from zope.interface import implementedBy
from zope.interface import directlyProvidedBy
from zope.interface import providedBy
from zope.interface import directlyProvides
from zope.interface.interfaces import IInterface
from zope.app.component.interface import getInterface
from zope.app.component.interface import searchInterface

from interfaces import IMarkerUtility

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
        return directlyProvidedBy(obj)

    def getDirectlyProvidedNames(self, obj):
        return self._getInterfaceNames(self.getDirectlyProvided(obj))

    def getAvailableInterfaces(self, obj):
        results = []
        todo = list(providedBy(obj))
        done = []
        while todo:
            interface = todo.pop()
            done.append(interface)
            for base in interface.__bases__:
                if base not in todo and base not in done:
                    todo.append(base)
            markers = self._getDirectMarkersOf(interface)
            for interface in markers:
                if (interface not in results
                    and not interface.providedBy(obj)):
                    results.append(interface)
            todo += markers
        return tuple(results)

    def getAvailableInterfaceNames(self, obj):
        names = self._getInterfaceNames(self.getAvailableInterfaces(obj))
        names.sort()
        return names

    def getInterfaces(self, obj):
        return tuple(implementedBy(obj.__class__))

    def getInterfaceNames(self, obj):
        return self._getInterfaceNames(self.getInterfaces(obj))

    def getProvided(self, obj):
        return providedBy(obj)

    def getProvidedNames(self, obj):
        return self._getInterfaceNames(self.getProvided(obj))

    def update(self, obj, add=(), remove=()):
        """Currently update adds and then removes, rendering duplicate null.
        """
        marker_ifaces = self.getAvailableInterfaces(obj)
        if len(add):
            [mark(obj, interface)
             for interface in Set(marker_ifaces) & Set(add)]

        direct_ifaces = self.getDirectlyProvided(obj)
        if len(remove):
            [erase(obj, interface)
             for interface in Set(direct_ifaces) & Set(remove)]

    def _getInterfaceNames(self, interfaces):
        return [interfaceToName(self, iface) for iface in interfaces]

    def _getDirectMarkersOf(self, base):
        """Get empty interfaces directly inheriting from the given one.
        """
        results = []
        interfaces = searchInterface(None, base=base)
        for interface in interfaces:
            # There are things registered with the interface service
            # that are not interfaces. Yay!
            if not IInterface.providedBy(interface):
                continue
            if base in interface.__bases__ and not interface.names():
                results.append(interface)
        results.sort()
        return tuple(results)


_utility = MarkerUtility()
def getMarkerUtility():
    return _utility


# BBB: for Zope 2.8/3.0, will be replaced in Five 1.3 by
#      from zope.app.component.interface import interfaceToName
def interfaceToName(context, interface):
    if interface is None:
        return 'None'
    items = searchInterface(context, base=interface)
    ids = [('%s.%s' %(iface.__module__, iface.__name__))
           for iface in items
           if iface == interface]

    if not ids:
        # Do not fail badly, instead resort to the standard
        # way of getting the interface name, cause not all interfaces
        # may be registered as utilities.
        return interface.__module__ + '.' + interface.__name__

    assert len(ids) == 1, "Ambiguous interface names: %s" % ids
    return ids[0]
