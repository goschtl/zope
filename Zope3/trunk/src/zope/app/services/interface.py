##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Code about services and interfaces.

This module contains code for interfaces in persistent modules, and
for the local interface service.

$Id: interface.py,v 1.17 2003/09/21 17:31:59 jim Exp $
"""

from persistence import Persistent
from zodb.code.patch import registerWrapper, Wrapper
from zope.interface.interface import InterfaceClass
from zope.interface.interfaces import IInterface
from zope.interface import Interface, providedBy
from zope.component import getService
from zope.app.component.nextservice import getNextService
from zope.app.interfaces.services.service import ISimpleService
from zope.app.interfaces.component import IInterfaceService
from zope.app import zapi
from zope.app.services.servicenames import Interfaces, Utilities
from zope.component import ComponentLookupError
from zope.interface import implements
from zope.app.container.contained import Contained
from zope.app.interfaces.services.registration import IRegistrationStack

class PersistentInterfaceClass(Persistent, InterfaceClass):
    pass

# PersistentInterface is equivalent to the zope.interface.Interface object
# except that it is also persistent.  It is used in conjunction with
# zodb.code to support interfaces in persistent modules.
PersistentInterface = PersistentInterfaceClass("PersistentInterface",
                                               (Interface, ))

class PersistentInterfaceWrapper(Wrapper):

    def unwrap(self):
        return PersistentInterfaceClass(self._obj.__name__)


registerWrapper(InterfaceClass, PersistentInterfaceWrapper,
                lambda iface: (),
                lambda iface: iface.__dict__,
                )


class LocalInterfaceService(Contained):
    """A local interface service."""

    implements(IInterfaceService,
               ISimpleService)

    def getInterface(self, id):
        # Return the interface registered for the given id
        i = self.queryInterface(id)
        if i is None:
            raise ComponentLookupError(id)
        return i

    def queryInterface(self, id, default=None):
        # Return the interface registered for the given id
        next = getNextService(self, Interfaces)
        iface = next.queryInterface(id, default)
        if iface is default:
            utilities = self._queryUtilityInterfaces(search_string=id)
            if utilities:
                return utilities[0][1]
            return default
        return iface

    def searchInterface(self, search_string="", base=None):
        # Return the interfaces that match the search criteria
        ifaces = {}
        next = getNextService(self, Interfaces)
        for iface in next.searchInterface(search_string, base):
            ifaces[iface] = None
        for item in self._queryUtilityInterfaces(base, search_string):
            if not ifaces.has_key(item[1]):
                ifaces[item[1]] = None
        return ifaces.keys()

    def searchInterfaceIds(self, search_string="", base=None):
        # Return the ids of the interfaces that match the search criteria.
        ids = {}
        next = getNextService(self, Interfaces)
        for id in next.searchInterfaceIds(search_string, base):
            ids[id] = None
        for item in self._queryUtilityInterfaces(base, search_string):
            if not ids.has_key(item[0]):
                ids[item[0]] = None
        return ids.keys()

    def items(self, search_string="", base=None):
        # Return id, interface pairs for all items matching criteria.
        items = {}
        next = getNextService(self, Interfaces)
        for item in next.items(search_string, base):
            items[item] = None
        for item in self._queryUtilityInterfaces(base, search_string):
            if not items.has_key(item):
                items[item] = None
        return items.keys()

    def _queryUtilityInterfaces(self, interface=None, search_string=None):
        utilities = getService(self, Utilities)
        matching = utilities.getUtilitiesFor(interface)
        matching = [m for m in matching
                    if IInterface in providedBy(m[1])]
        if search_string is not None:
            return [match for match in matching
                    if match[0].find(search_string) > -1]
        return matching

