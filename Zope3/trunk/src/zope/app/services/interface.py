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
"""

from persistence import Persistent
from zodb.code.patch import registerWrapper, Wrapper
from zope.interface.interface import InterfaceClass

from zope.app.component.nextservice import getNextService
from zope.app.interfaces.services.service import ISimpleService
from zope.app.interfaces.component import IInterfaceService
from zope.app import zapi
from zope.app.services.servicenames import Interfaces
from zope.component import ComponentLookupError
from zope.interface import implements

class PersistentInterfaceClass(Persistent, InterfaceClass):
    pass

# PersistentInterface is equivalent to the zope.interface.Interface object
# except that it is also persistent.  It is used in conjunction with
# zodb.code to support interfaces in persistent modules.
PersistentInterface = PersistentInterfaceClass("PersistentInterface")

class PersistentInterfaceWrapper(Wrapper):

    def unwrap(self):
        return PersistentInterfaceClass(self._obj.__name__)

def register(): # XXX has been refactored on a branch
    registerWrapper(InterfaceClass, PersistentInterfaceWrapper,
                    lambda iface: (),
                    lambda iface: iface.__dict__,
                    )

class LocalInterfaceService(object):
    """I need a doc string."""
    
    implements(IInterfaceService,
               ISimpleService)

    # All the methods defined here are context methods
    zapi.ContextAwareDescriptors()
    
    def getInterface(self, id):
        # Return the interface registered for the given id
        i = self.queryInterface(id)
        if i is None:
            raise ComponentLookupError(id)
        return i

    def queryInterface(self, id, default=None):
        # Return the interface registered for the given id
        next = getNextService(self, Interfaces)
        return next.queryInterface(id, default)

    def searchInterface(self, search_string="", base=None):
        # Return the interfaces that match the search criteria
        next = getNextService(self, Interfaces)
        return next.searchInterface(search_string, base)

    def searchInterfaceIds(self, search_string="", base=None):
        # Return the ids of the interfaces that match the search criteria.
        next = getNextService(self, Interfaces)
        return next.searchInterfaceIds(search_string, base)

    def items(self, search_string="", base=None):
        # Return id, interface pairs for all items matching criteria.
        next = getNextService(self, Interfaces)
        return next.items(search_string, base)
