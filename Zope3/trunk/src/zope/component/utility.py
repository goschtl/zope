##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""utility service

$Id: utility.py,v 1.8 2004/03/05 22:09:25 jim Exp $
"""

from zope.interface.implementor import ImplementorRegistry
from zope.interface import implements
from zope.component.interfaces import IUtilityService
from zope.component.exceptions import Invalid, ComponentLookupError

class IGlobalUtilityService(IUtilityService):

    def provideUtility(providedInterface, component, name=''):
        """Provide a utility

        A utility is a component that provides an interface.
        """

class GlobalUtilityService:

    implements(IGlobalUtilityService)

    def __init__(self):
        self.__utilities = {}

    def provideUtility(self, providedInterface, component, name=''):
        """See IGlobalUtilityService interface"""

        if not providedInterface.providedBy(component):
            raise Invalid("The registered component doesn't implement "
                          "the promised interface.")

        registry = self.__utilities.get(name)
        if registry is None:
            registry = ImplementorRegistry()
            self.__utilities[name] = registry

        registry.register(providedInterface, component)

    def getUtility(self, interface, name=''):
        """See IUtilityService interface"""
        c = self.queryUtility(interface, None, name)
        if c is not None:
            return c
        raise ComponentLookupError(interface)

    def queryUtility(self, interface, default=None, name=''):
        """See IUtilityService interface"""

        registry = self.__utilities.get(name)
        if registry is None:
            return default

        c = registry.get(interface)
        if c is not None:
            return c

        return default

    def getRegisteredMatching(self, interface=None, name=None):
        L = []
        for reg_name in self.__utilities:
            for iface, c in self.__utilities[reg_name].getRegisteredMatching():
                if c is None:
                    continue
                if interface and not iface is interface:
                    continue
                if name is not None and reg_name.find(name) < 0:
                    continue
                L.append((iface, reg_name, c))
        return L

    def getUtilitiesFor(self, interface=None):
        utilities = {}
        for name in self.__utilities:
            for iface, util in self.__utilities[name].getRegisteredMatching():
                if util is None:
                    continue
                if interface and not iface.extends(interface, 0) and \
                       util is not interface:
                    continue
                utilities[(name, util)] = None

        return utilities.keys()

    _clear = __init__

# the global utility service instance (see component.zcml )
utilityService = GlobalUtilityService()
_clear         = utilityService._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
