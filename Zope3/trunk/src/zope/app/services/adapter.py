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

$Id: adapter.py,v 1.7 2003/02/06 06:49:56 seanb Exp $
"""
__metaclass__ = type

from zope.interface.adapter import AdapterRegistry
from persistence import Persistent
from persistence.dict import PersistentDict
from zope.component.interfaces import IAdapterService
from zope.component.exceptions import ComponentLookupError
from zope.component import getServiceManager
from zope.component.servicenames import Adapters
from zope.app.interfaces.services.configuration import IConfigurable
from zope.app.services.configuration import ConfigurationRegistry
from zope.app.services.configuration import SimpleConfiguration
from zope.proxy.context import ContextWrapper
from zope.proxy.context import ContextMethod
from zope.app.services.configuration import ConfigurationStatusProperty
from zope.app.component.nextservice import getNextService

from zope.app.interfaces.services.interfaces import IAdapterConfiguration

class PersistentAdapterRegistry(Persistent, AdapterRegistry):

    def __init__(self):
        AdapterRegistry.__init__(self, PersistentDict())


class AdapterService(Persistent):

    __implements__ = IAdapterService, IConfigurable

    def __init__(self):
        self._byName = PersistentDict()

    def queryConfigurationsFor(self, configuration, default=None):
        "See IConfigurable"
        # XXX Need to add named adapter support
        return self.queryConfigurations(
            configuration.forInterface, configuration.providedInterface,
            configuration.adapterName,
            default)

    queryConfigurationsFor = ContextMethod(queryConfigurationsFor)

    def queryConfigurations(self,
                            forInterface, providedInterface, adapterName,
                            default=None):

        adapters = self._byName.get(adapterName)
        if adapters is None:
            return default

        registry = adapters.getRegistered(forInterface, providedInterface)
        if registry is None:
            return default

        return ContextWrapper(registry, self)

    queryConfigurations = ContextMethod(queryConfigurations)

    def createConfigurationsFor(self, configuration):
        "See IConfigurable"
        # XXX Need to add named adapter support
        return self.createConfigurations(
            configuration.forInterface, configuration.providedInterface,
            configuration.adapterName)

    createConfigurationsFor = ContextMethod(createConfigurationsFor)

    def createConfigurations(self, forInterface, providedInterface, name):

        adapters = self._byName.get(name)
        if adapters is None:
            adapters = PersistentAdapterRegistry()
            self._byName[name] = adapters

        registry = adapters.getRegistered(forInterface, providedInterface)
        if registry is None:
            registry = ConfigurationRegistry()
            adapters.register(forInterface, providedInterface, registry)

        return ContextWrapper(registry, self)

    createConfigurations = ContextMethod(createConfigurations)

    def getAdapter(self, object, interface, name=''):
        "See IAdapterService"
        adapter = self.queryAdapter(object, interface, None, name)
        if adapter is None:
            raise ComponentLookupError(object, interface)
        return adapter

    getAdapter = ContextMethod(getAdapter)

    def queryAdapter(self, object, interface, default=None, name=''):
        "See IAdapterService"
        if not name and interface.isImplementedBy(object):
            return object

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

        return adapters.queryAdapter(object, interface, default)

    queryAdapter = ContextMethod(queryAdapter)

    # XXX need to add name support
    def getRegisteredMatching(self,
                              for_interfaces=None,
                              provided_interfaces=None):

        adapters = self._byName.get('')
        if adapters is None:
            return ()

        return adapters.getRegisteredMatching(for_interfaces,
                                              provided_interfaces)

class AdapterConfiguration(SimpleConfiguration):

    __implements__ = IAdapterConfiguration, SimpleConfiguration.__implements__

    status = ConfigurationStatusProperty(Adapters)

    # XXX These should be positional arguments, except that forInterface
    #     isn't passed in if it is omitted. To fix this, we need a
    #     required=False,explicitly_unrequired=True in the schema field
    #     so None will get passed in.
    def __init__(self, forInterface=None, providedInterface=None,
                 factoryName=None, adapterName=u''):
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
