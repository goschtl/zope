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

__metaclass__ = type
import sys
from zope.interface import implements
from zope.interface.adapter import AdapterRegistry
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IGlobalAdapterService
import warnings

class GlobalAdapterService:

    implements(IGlobalAdapterService)

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
        result = self.queryAdapter(object, interface, name=name)
        if result is None:
            raise ComponentLookupError(object, interface)

        return result

    def getNamedAdapter(self, object, interface, name):
        """see IAdapterService interface"""
        result = self.queryNamedAdapter(object, interface, name)
        if result is None:
            raise ComponentLookupError(object, interface)

        return result


    def queryAdapter(self, object, interface, default=None, name=''):
        """see IAdapterService interface"""
        if name:
            warnings.warn("The name argument to queryAdapter is deprecated",
                          DeprecationWarning, 2)
            return self.queryNamedAdapter(object, interface, name, default)

        conform = getattr(object, '__conform__', None)
        if conform is not None:
            try:
                adapter = conform(interface)
            except TypeError:
                # We got a TypeError. It might be an error raised by
                # the __conform__ implementation, or *we* may have
                # made the TypeError by calling an unbound method
                # (object is a class).  In the later case, we behave
                # as though there is no __conform__ method. We can
                # detect this case by checking whether there is more
                # than one traceback object in the traceback chain:
                if sys.exc_info()[2].tb_next is not None:
                    # There is more than one entry in the chain, so
                    # reraise the error:
                    raise
                # This clever trick is from Phillip Eby
            else:
                if adapter is not None:
                    return adapter

        if interface.isImplementedBy(object):
            return object

        return self.queryNamedAdapter(object, interface, name, default)

    def queryNamedAdapter(self, object, interface, name, default=None):
        """see IAdapterService interface"""
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
try:
    from zope.testing.cleanup import addCleanUp
except ImportError:
    pass
else:
    addCleanUp(_clear)
    del addCleanUp
