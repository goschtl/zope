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
"""adapter service
"""

from zope.interface.adapter import AdapterRegistry
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IAdapterService

class IGlobalAdapterService(IAdapterService):

    def provideAdapter(forInterface, providedInterface, maker, name=''):
        """Provide an adapter

        An adapter provides an interface for objects that have another
        interface.

        Arguments:

        forInterface -- The interface the adapter provides an interface for.

        providedInterface -- The provided interface

        maker -- a callable object that gets an adapter component for
        a context component.
        """
    def getRegisteredMatching(for_interface=None, provide_interface=None,
                              name=None):
        """Return information about registered data

        A four-tuple is returned containing:

          - registered name,

          - registered for interface

          - registered provided interface, and

          - registered data
        """

class GlobalAdapterService:

    __implements__ = IGlobalAdapterService

    def __init__(self):
        self.__adapters = {}

    def provideAdapter(self, forInterface, providedInterface, maker, name=''):
        """see IGlobalAdapterService interface"""

        if not isinstance(maker, (list, tuple)):
            maker = [maker]
        else:
            maker = list(maker)

        if not maker == filter(callable, maker):
            raise TypeError("The registered component callable is not "
                            "callable")

        registry = self.__adapters.get(name)
        if registry is None:
            registry = AdapterRegistry()
            self.__adapters[name] = registry

        registry.register(forInterface, providedInterface, maker)

    def getAdapter(self, object, interface, name=''):
        """see IAdapterService interface"""
        result = self.queryAdapter(object, interface, None, name)
        if result is None:
            raise ComponentLookupError(object, interface)

        return result


    def queryAdapter(self, object, interface, default=None, name=''):
        """see IAdapterService interface"""
        if (not name) and interface.isImplementedBy(object):
            return object

        registry = self.__adapters.get(name)
        if registry is None:
            return default

        makers = registry.getForObject(object, interface)

        if makers is None:
            return default

        result = object
        for maker in makers:
            result = maker(result)

        return result

    def getRegisteredMatching(self,
                              for_interfaces=None,
                              provided_interfaces=None,
                              name = None,
                              ):

        if name is not None:
            registry = self.__adapters.get(name)
            if registry is None:
                return ()
            return [(name, for_, provided, data)
                    for (for_, provided, data)
                    in registry.getRegisteredMatching(for_interfaces,
                                                      provided_interfaces)
                    ]

        result = []
        for name in self.__adapters:
            r = self.getRegisteredMatching(
                for_interfaces, provided_interfaces, name)
            result.extend(r)

        return result

    _clear = __init__

# the global adapter service instance (see component.zcml )
adapterService = GlobalAdapterService()
provideAdapter = adapterService.provideAdapter



_clear = adapterService._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
