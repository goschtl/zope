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

$Id: utility.py,v 1.4 2003/06/04 09:09:45 stevea Exp $
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

        if not providedInterface.isImplementedBy(component):
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
        if c is None:
            raise ComponentLookupError(interface)
        return c

    def queryUtility(self, interface, default=None, name=''):
        """See IUtilityService interface"""

        registry = self.__utilities.get(name)
        if registry is None:
            return default

        c = registry.get(interface)
        if c is None:
            c = default

        return c

    _clear = __init__

# the global utility service instance (see component.zcml )
utilityService = GlobalUtilityService()




_clear         = utilityService._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
