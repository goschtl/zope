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
"""XXX I need a summary line.

In addition, a ServiceManager acts as a registry for persistent
modules.  The Zope import hook uses the ServiceManager to search for
modules.

$Id: ServiceManager.py,v 1.10 2002/11/30 18:39:17 jim Exp $
"""

import sys

from Zope.Exceptions import NotFoundError, ZopeError

from Zope.App.ComponentArchitecture.IServiceManagerContainer \
     import IServiceManagerContainer
from Zope.ComponentArchitecture import getService, queryAdapter
from Zope.App.ComponentArchitecture.NextService \
     import getNextServiceManager, getNextService
from Zope.ComponentArchitecture.GlobalServiceManager import UndefinedService
from Zope.ComponentArchitecture.GlobalServiceManager import InvalidService
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError

from Zope.App.OFS.Container.IContainer import ISimpleReadContainer
from Zope.App.OFS.Content.Folder.Folder import Folder
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.App.OFS.Container.BTreeContainer import BTreeContainer
from Zope.Proxy.ProxyIntrospection import removeAllProxies

from Packages import Packages
from IServiceManager import IServiceManager

from Zope.App.OFS.Services.Configuration import ConfigurationRegistry

from Persistence.Module import PersistentModuleRegistry
from Persistence.Module import PersistentModuleRegistry, PersistentModule
from INameResolver import INameResolver

ModuleType = type(INameResolver)
ModuleType = ModuleType, PersistentModule


class ServiceManager(PersistentModuleRegistry):

    __implements__ = (IServiceManager, ISimpleReadContainer,
                      PersistentModuleRegistry.__implements__,
                      INameResolver)

    def __init__(self):
        super(ServiceManager, self).__init__()

        self.__bindings = {}
        # Bindings is of the form:
        #
        # {service_type -> ConfigurationRegistry}

        self.Packages = Packages()


    def getServiceDefinitions(self):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"

        # Get the services defined here and above us, if any (as held
        # in a ServiceInterfaceService, presumably)
        sm = getNextServiceManager(self)
        if sm is not None:
            serviceDefs = sm.getServiceDefinitions()
        else: serviceDefs = {}

        return serviceDefs

    getServiceDefinitions = ContextMethod(getServiceDefinitions)

    def queryService(self, name, default=None):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        try:
            return self.getService(name)
        except ComponentLookupError:
            return default

    queryService = ContextMethod(queryService)

    def getService(self, name):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"

        # This is rather tricky. Normally, getting a service requires
        # the use of other services, like the adapter service.  We
        # need to be careful not to get into an infinate recursion by
        # getting out getService to be called while looking up
        # services, so we'll

        if name == 'Services':
            return self # We are the service service

        if not getattr(self, '_v_calling', 0):
            
            self._v_calling = 1
            try:
                service = self.getBoundService(name)
                if service:
                    return service
                    
            finally:
                self._v_calling = 0

        return getNextService(self, name)

    getService = ContextMethod(getService)


    def getInterfaceFor(self, service_type):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        for type, interface in self.getServiceDefinitions():
            if type == service_type:
                return interface

        raise NameError(service_type)

    getInterfaceFor = ContextMethod(getInterfaceFor)

    def queryConfigurationsFor(self, configuration, default=None):
        return self.queryConfigurations(configuration.serviceType, default)

    queryConfigurationsFor = ContextMethod(queryConfigurationsFor)

    def queryConfigurations(self, service_type, default=None):
        registry = self.__bindings.get(service_type, default)
        return ContextWrapper(registry, self)

    queryConfigurations = ContextMethod(queryConfigurations)
        

    def createConfigurationsFor(self, configuration):
        return self.createConfigurations(configuration.serviceType)

    createConfigurationsFor = ContextMethod(createConfigurationsFor)

    def createConfigurations(self, service_type):
        registry = ConfigurationRegistry()
        self.__bindings[service_type] = registry
        self._p_changed = 1
        return registry

    createConfigurations = ContextMethod(createConfigurations)

    def getBoundService(self, name):
        "See Zope.App.OFS.Services.ServiceManager.IServiceManager."

        registry = self.queryConfigurations(name)
        if registry:
            configuration = registry.active()
            if configuration is not None:
                service = configuration.getService()
                return service
            
        return None

    getBoundService = ContextMethod(getBoundService)

    def getBoundServiceTypes(self):
        "See "
        "Zope.App.OFS.Services.ServiceManager.IServiceManager.IServiceManager"
        
        return  self.__bindings.keys()

    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.Services.ServiceManager.IComponentManager.

    def queryComponent(self, type=None, filter=None, all=0):
        Packages = ContextWrapper(self.Packages, self, name='Packages')
        return Packages.queryComponent(type, filter, all)

    queryComponent = ContextMethod(queryComponent)

    #
    ############################################################


    # We provide a mapping interface for traversal, but we only expose
    # local services through the mapping interface.

    def __getitem__(self, key):
        "See Interface.Common.Mapping.IReadMapping"

        result = self.get(key)
        if result is None:
            raise KeyError(key)

        return result

    def get(self, key, default=None):
        "See Interface.Common.Mapping.IReadMapping"

        if key == 'Packages':
            return self.Packages

        directives = self.__bindings.get(key)
        if directives and directives[0] is not None:
            return self.queryService(key, default)

        return default

    get = ContextMethod(get)

    def __contains__(self, key):
        "See Interface.Common.Mapping.IReadMapping"

        return self.get(key) is not None

    def findModule(self, name):
        # override to pass call up to next service manager 
        mod = super(ServiceManager, removeAllProxies(self)).findModule(name)
        if mod is not None:
            return mod
        
        sm = getNextServiceManager(self)
        try:
            findModule = sm.findModule
        except AttributeError:
            # The only service manager that doesn't implement this
            # interface is the global service manager.  There is no
            # direct way to ask if sm is the global service manager.
            return None
        return findModule(name)

    findModule = ContextMethod(findModule)

    def __import(self, module_name):

        mod = self.findModule(module_name)
        if mod is None:
            mod = sys.modules.get(module_name)
            if mod is None:
                raise ImportError(module_name)

        return mod

    __import = ContextMethod(__import)

    def resolve(self, name):
        
        name = name.strip()

        if name.endswith('.') or name.endswith('+'):
            name = name[:-1]
            repeat = 1
        else:
            repeat = 0

        names=name.split('.')
        last=names[-1]
        mod='.'.join(names[:-1])

        if not mod:
            return self.__import(name)

        while 1:
            m = self.__import(mod)
            try:
                a=getattr(m, last)
            except AttributeError:
                if not repeat:
                    return self.__import(name)

            else:
                if not repeat or (not isinstance(a, ModuleType)):
                    return a
            mod += '.' + last

    resolve = ContextMethod(resolve)

