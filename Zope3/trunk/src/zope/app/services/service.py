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
"""Service manager implementation

A service manager has a number of roles:

  - A service service

  - A place to do TTW development or to manage database-based code

  - A registry for persistent modules.  The Zope import hook uses the
    ServiceManager to search for modules.  (This functionality will
    eventually be replaced by a separate module service.)

$Id: service.py,v 1.15 2003/03/23 16:45:44 jim Exp $
"""

import sys

from zodb.code.module import PersistentModule
from zodb.code.module import PersistentModuleRegistry

from zope.component import getAdapter
from zope.component import getServiceManager
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IServiceService

from zope.proxy.context import ContextMethod
from zope.proxy.context import ContextWrapper
from zope.proxy.introspection import removeAllProxies

from zope.app.component.nextservice import getNextService
from zope.app.component.nextservice import getNextServiceManager

from zope.app.interfaces.container import IContainer
from zope.app.interfaces.services.service import IBindingAware
from zope.app.interfaces.services.module import IModuleService
from zope.app.interfaces.services.service import IServiceConfiguration
from zope.app.interfaces.services.service import IServiceManager
from zope.app.interfaces.services.service import IServiceManagerContainer
from zope.app.interfaces.services.configuration import IUseConfiguration

# XXX This makes no sense?
ModuleType = type(IModuleService), PersistentModule

from zope.app.services.configuration import ConfigurationStatusProperty
from zope.app.services.configuration import NameComponentConfigurable
from zope.app.services.configuration import NamedComponentConfiguration
from zope.app.services.folder import SiteManagementFolders
from zope.app.interfaces.services.configuration import IUseConfigurable
from zope.app.interfaces.services.service import ILocalService

from zope.app.traversing import getPath

class ServiceManager(PersistentModuleRegistry, NameComponentConfigurable):

    __implements__ = (IServiceManager, IContainer,
                      PersistentModuleRegistry.__implements__,
                      NameComponentConfigurable.__implements__,
                      IModuleService)

    def __init__(self):
        super(ServiceManager, self).__init__()
        NameComponentConfigurable.__init__(self)
        self.Packages = SiteManagementFolders()

    def getServiceDefinitions(wrapped_self):
        "See IServiceService"

        # Get the services defined here and above us, if any (as held
        # in a ServiceInterfaceService, presumably)
        sm = getNextServiceManager(wrapped_self)
        if sm is not None:
            serviceDefs = sm.getServiceDefinitions()
        else: serviceDefs = {}

        return serviceDefs
    getServiceDefinitions = ContextMethod(getServiceDefinitions)

    def queryService(wrapped_self, name, default=None):
        "See IServiceService"
        try:
            return wrapped_self.getService(name)
        except ComponentLookupError:
            return default
    queryService = ContextMethod(queryService)

    def getService(wrapped_self, name):
        "See IServiceService"

        # This is rather tricky. Normally, getting a service requires
        # the use of other services, like the adapter service.  We
        # need to be careful not to get into an infinate recursion by
        # getting out getService to be called while looking up
        # services, so we'll

        if name == 'Services':
            return wrapped_self # We are the service service

        if not getattr(wrapped_self, '_v_calling', 0):

            wrapped_self._v_calling = 1
            try:
                service = wrapped_self.queryActiveComponent(name)
                if service is not None:
                    return service

            finally:
                wrapped_self._v_calling = 0

        return getNextService(wrapped_self, name)
    getService = ContextMethod(getService)


    def getInterfaceFor(wrapped_self, service_type):
        "See IServiceService"
        for type, interface in wrapped_self.getServiceDefinitions():
            if type == service_type:
                return interface

        raise NameError(service_type)
    getInterfaceFor = ContextMethod(getInterfaceFor)

    def queryComponent(self, type=None, filter=None, all=0):
        local = []
        path = getPath(self)
        for pkg_name in self:
            package = ContextWrapper(self[pkg_name], self, name=pkg_name)
            for name in package:
                component = package[name]
                if type is not None and not type.isImplementedBy(component):
                    continue
                if filter is not None and not filter(component):
                    continue
                wrapper =  ContextWrapper(component, package, name=name)
                local.append({'path': "%s/%s/%s" % (path, pkg_name, name),
                              'component': wrapper,
                              })

        if all:
            next_service_manager = getNextServiceManager(self)
            if IComponentManager.isImplementedBy(next_service_manager):
                next_service_manager.queryComponent(type, filter, all)

            local += list(all)

        return local

    queryComponent = ContextMethod(queryComponent)

    # We provide a mapping interface for traversal, but we only expose
    # local services through the mapping interface.

    def __getitem__(self, key):
        "See Interface.Common.Mapping.IReadMapping"

        result = self.get(key)
        if result is None:
            raise KeyError(key)

        return result

    def get(wrapped_self, key, default=None):
        "See Interface.Common.Mapping.IReadMapping"

        if key == 'Packages':
            return wrapped_self.Packages

        return wrapped_self.Packages.get(key, default)

    get = ContextMethod(get)

    def __contains__(self, key):
        "See Interface.Common.Mapping.IReadMapping"

        return self.get(key) is not None

    def __iter__(self):
        return iter(self.keys())

    def keys(self):
        return self.Packages.keys()

    def values(self):
        return map(self.get, self.keys())

    values = ContextMethod(values)

    def items(self):
        return [(key, self.get(key)) for key in self.keys()]

    items = ContextMethod(items)

    def __len__(self):
        return len(self.Packages)

    def setObject(self, name, value):
        return self.Packages.setObject(name, value)

    def findModule(wrapped_self, name):
        # override to pass call up to next service manager
        mod = super(ServiceManager,
                    removeAllProxies(wrapped_self)).findModule(name)
        if mod is not None:
            return mod

        sm = getNextServiceManager(wrapped_self)
        try:
            findModule = sm.findModule
        except AttributeError:
            # The only service manager that doesn't implement this
            # interface is the global service manager.  There is no
            # direct way to ask if sm is the global service manager.
            return None
        return findModule(name)
    findModule = ContextMethod(findModule)

    def __import(wrapped_self, module_name):

        mod = wrapped_self.findModule(module_name)
        if mod is None:
            mod = sys.modules.get(module_name)
            if mod is None:
                raise ImportError(module_name)

        return mod
    __import = ContextMethod(__import)

    def resolve(wrapped_self, name):

        name = name.strip()

        if name.endswith('.') or name.endswith('+'):
            name = name[:-1]
            repeat = 1
        else:
            repeat = 0

        names = name.split('.')
        last = names[-1]
        mod = '.'.join(names[:-1])

        if not mod:
            return wrapped_self.__import(name)

        while 1:
            m = wrapped_self.__import(mod)
            try:
                a = getattr(m, last)
            except AttributeError:
                if not repeat:
                    return wrapped_self.__import(name)

            else:
                if not repeat or (not isinstance(a, ModuleType)):
                    return a
            mod += '.' + last
    resolve = ContextMethod(resolve)


class ServiceConfiguration(NamedComponentConfiguration):

    __doc__ = IServiceConfiguration.__doc__

    __implements__ = (IServiceConfiguration,
                      NamedComponentConfiguration.__implements__)

    status = ConfigurationStatusProperty('Services')

    label = "Service"

    def __init__(self, name, path, context=None):
        super(ServiceConfiguration, self).__init__(name, path)
        if context is not None:
            # Check that the object implements stuff we need
            wrapped_self = ContextWrapper(self, context)
            service = wrapped_self.getComponent()
            if not ILocalService.isImplementedBy(service):
                raise TypeError("service %r doesn't implement ILocalService" %
                                service)
        # Else, this must be a hopeful test invocation

    def getInterface(self):
        service_manager = getServiceManager(self)
        return service_manager.getInterfaceFor(self.name)

    getInterface = ContextMethod(getInterface)

    def activated(self):
        service = self.getComponent()
        if IBindingAware.isImplementedBy(service):
            service.bound(self.name)

    activated = ContextMethod(activated)

    def deactivated(self):
        service = self.getComponent()
        if IBindingAware.isImplementedBy(service):
            service.unbound(self.name)

    deactivated = ContextMethod(deactivated)

    def usageSummary(self):
        return self.name + " Service"

    def afterAddHook(self, configuration, container):
        NamedComponentConfiguration.afterAddHook(self,
                                                 configuration,
                                                 container)
        service = configuration.getComponent()
        adapter = getAdapter(service, IUseConfiguration)
        adapter.addUsage(getPath(configuration))

    def beforeDeleteHook(self, configuration, container):
        service = configuration.getComponent()
        adapter = getAdapter(service, IUseConfiguration)
        adapter.removeUsage(getPath(configuration))
        NamedComponentConfiguration.beforeDeleteHook(self,
                                                     configuration,
                                                     container)
