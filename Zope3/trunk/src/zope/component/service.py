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
"""

$Id: service.py,v 1.3 2002/12/28 01:42:21 rdmurray Exp $
"""

from zope.exceptions import DuplicationError
from zope.component.interfaces import IServiceService
from zope.component.exceptions import ComponentLookupError


class IGlobalServiceManager(IServiceService):

    def defineService(name, interface):
        """Define a new service of the given name implementing the given
        interface.  If the name already exists, raises
        DuplicationError"""

    def provideService(name, component):
        """Register a service component.

        Provide a service component to do the work of the named
        service.  If a service component has already been assigned to
        this name, raise DuplicationError; if the name has not been
        defined, raises UndefinedService; if the component does not
        implement the registered interface for the service name,
        raises InvalidService.

        """

class UndefinedService(Exception):
    """An attempt to register a service that has not been defined
    """

class InvalidService(Exception):
    """An attempt to register a service that doesn't implement
       the required interface
    """

class GlobalServiceManager:
    """service manager"""

    __implements__ = IGlobalServiceManager

    def __init__(self):
        self.__defs     = {}
        self.__services = {}

    def defineService(self, name, interface):
        """see IGlobalServiceManager interface"""

        if name in self.__defs:
            raise DuplicationError(name)

        self.__defs[name] = interface

    def getServiceDefinitions(self):
        """see IServiceService Interface"""
        return self.__defs.items()

    def provideService(self, name, component, force=False):
        """see IGlobalServiceManager interface, above
        
        The force keyword allows one to replace an existing
        service.  This is mostly useful in testing scenarios.
        """

        if not force and name in self.__services:
            raise DuplicationError(name)

        if name not in self.__defs:
            raise UndefinedService(name)

        if not self.__defs[name].isImplementedBy(component):
            raise InvalidService(name, component, self.__defs[name])

        self.__services[name] = component

    def getService(self, name):
        """see IServiceService interface"""
        service = self.queryService(name)
        if service is None:
            raise ComponentLookupError(name)

        return service

    def queryService(self, name, default=None):
        """see IServiceService interface"""

        return self.__services.get(name, default)

    _clear = __init__


serviceManager = GlobalServiceManager() # the global service manager instance
defineService = serviceManager.defineService


_clear         = serviceManager._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
