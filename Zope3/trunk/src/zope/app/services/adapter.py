##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Adapter Service

$Id: adapter.py,v 1.19 2003/06/21 21:22:12 jim Exp $
"""
__metaclass__ = type

import sys
from zope.interface.adapter import AdapterRegistry
from persistence import Persistent
from persistence.dict import PersistentDict
from zope.interface import implements
from zope.component.interfaces import IAdapterService
from zope.component.exceptions import ComponentLookupError
from zope.component import getServiceManager
from zope.app.services.servicenames import Adapters
from zope.app.interfaces.services.registration import IRegistry
from zope.app.services.registration import RegistrationStack
from zope.app.services.registration import SimpleRegistration
from zope.app.context import ContextWrapper
from zope.context import ContextMethod
from zope.app.services.registration import RegistrationStatusProperty
from zope.app.component.nextservice import getNextService
from zope.app.interfaces.services.service import ISimpleService

from zope.app.interfaces.services.adapter import IAdapterRegistration

class PersistentAdapterRegistry(Persistent, AdapterRegistry):

    def __init__(self):
        AdapterRegistry.__init__(self, PersistentDict())


class AdapterService(Persistent):

    implements(IAdapterService, IRegistry, ISimpleService)

    def __init__(self):
        self._byName = PersistentDict()

    def queryRegistrationsFor(self, registration, default=None):
        "See IRegistry"
        # XXX Need to add named adapter support
        return self.queryRegistrations(
            registration.forInterface, registration.providedInterface,
            registration.adapterName,
            default)

    queryRegistrationsFor = ContextMethod(queryRegistrationsFor)

    def queryRegistrations(self,
                            forInterface, providedInterface, adapterName,
                            default=None):

        adapters = self._byName.get(adapterName)
        if adapters is None:
            return default

        registry = adapters.getRegistered(forInterface, providedInterface)
        if registry is None:
            return default

        return ContextWrapper(registry, self)

    queryRegistrations = ContextMethod(queryRegistrations)

    def createRegistrationsFor(self, registration):
        "See IRegistry"
        # XXX Need to add named adapter support
        return self.createRegistrations(
            registration.forInterface, registration.providedInterface,
            registration.adapterName)

    createRegistrationsFor = ContextMethod(createRegistrationsFor)

    def createRegistrations(self, forInterface, providedInterface, name):

        adapters = self._byName.get(name)
        if adapters is None:
            adapters = PersistentAdapterRegistry()
            self._byName[name] = adapters

        registry = adapters.getRegistered(forInterface, providedInterface)
        if registry is None:
            registry = RegistrationStack()
            adapters.register(forInterface, providedInterface, registry)

        return ContextWrapper(registry, self)

    createRegistrations = ContextMethod(createRegistrations)

    def getAdapter(self, object, interface, name=''):
        "See IAdapterService"
        adapter = self.queryAdapter(object, interface, name=name)
        if adapter is None:
            raise ComponentLookupError(object, interface)
        return adapter

    getAdapter = ContextMethod(getAdapter)

    def getNamedAdapter(self, object, interface, name):
        "See IAdapterService"
        adapter = self.queryNamedAdapter(object, interface, name)
        if adapter is None:
            raise ComponentLookupError(object, interface)
        return adapter

    getNamedAdapter = ContextMethod(getNamedAdapter)

    def queryAdapter(self, object, interface, default=None, name=''):
        """see IAdapterService interface"""
        if name:
            warnings.warn("The name argument to queryAdapter is deprecated",
                          DeprecationWarning, 2)
            return queryNamedAdapter(object, interface, name, default, context)
    
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

    queryAdapter = ContextMethod(queryAdapter)

    def queryNamedAdapter(self, object, interface, name, default=None):
        adapters = self._byName.get(name)

        if adapters:
            registry = adapters.getForObject(
                object, interface,
                filter = lambda registry:
                         ContextWrapper(registry, self).active(),
                )

            if registry is not None:
                registry = ContextWrapper(registry, self)
                adapter = registry.active().getAdapter(object)
                return adapter

        adapters = getNextService(self, Adapters)

        return adapters.queryNamedAdapter(object, interface, name, default)

    queryNamedAdapter = ContextMethod(queryNamedAdapter)

    # XXX need to add name support
    def getRegisteredMatching(self,
                              for_interfaces=None,
                              provided_interfaces=None):

        adapters = self._byName.get('')
        if adapters is None:
            return ()

        return adapters.getRegisteredMatching(for_interfaces,
                                              provided_interfaces)

class AdapterRegistration(SimpleRegistration):

    implements(IAdapterRegistration)

    serviceType = Adapters

    status = RegistrationStatusProperty()

    # XXX These should be positional arguments, except that forInterface
    #     isn't passed in if it is omitted. To fix this, we need a
    #     required=False,explicitly_unrequired=True in the schema field
    #     so None will get passed in.
    def __init__(self, forInterface=None, providedInterface=None,
                 factoryName=None, adapterName=u'',
                 # XXX The permission isn't plumbed. We're going to
                 # redo all of this anyway.  
                 permission=None,
                 ):
        if None in (providedInterface, factoryName):
            raise TypeError(
                "Must provide 'providedInterface' and 'factoryName'")
        self.forInterface = forInterface
        self.providedInterface = providedInterface
        self.adapterName = adapterName
        self.factoryName = factoryName

    def getAdapter(self, object):
        sm = getServiceManager(self)
        factory = sm.resolve(self.factoryName)
        return factory(object)

    getAdapter = ContextMethod(getAdapter)

# XXX Pickle backward compatability
AdapterConfiguration = AdapterRegistration
