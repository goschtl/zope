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

$Id: ServiceManager.py,v 1.16 2002/12/18 20:23:05 stevea Exp $
"""

import sys

from Zope.App.ComponentArchitecture.NextService \
     import getNextServiceManager, getNextService
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError

from Zope.App.OFS.Container.IContainer import ISimpleReadContainer
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Proxy.ProxyIntrospection import removeAllProxies

from Packages import Packages
from IServiceManager import IServiceManager

from Zope.App.OFS.Services.Configuration import NameComponentConfigurable

from Persistence.Module import PersistentModuleRegistry
from Persistence.Module import PersistentModule
from INameResolver import INameResolver

ModuleType = type(INameResolver)
ModuleType = ModuleType, PersistentModule


class ServiceManager(PersistentModuleRegistry, NameComponentConfigurable):

    __implements__ = (IServiceManager, ISimpleReadContainer,
                      PersistentModuleRegistry.__implements__,
                      NameComponentConfigurable.__implements__,
                      INameResolver)

    def __init__(self):
        super(ServiceManager, self).__init__()
        NameComponentConfigurable.__init__(self)
        self.Packages = Packages()

    def getServiceDefinitions(wrapped_self):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"

        # Get the services defined here and above us, if any (as held
        # in a ServiceInterfaceService, presumably)
        sm = getNextServiceManager(wrapped_self)
        if sm is not None:
            serviceDefs = sm.getServiceDefinitions()
        else: serviceDefs = {}

        return serviceDefs
    getServiceDefinitions = ContextMethod(getServiceDefinitions)

    def queryService(wrapped_self, name, default=None):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        try:
            return wrapped_self.getService(name)
        except ComponentLookupError:
            return default
    queryService = ContextMethod(queryService)

    def getService(wrapped_self, name):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"

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
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        for type, interface in wrapped_self.getServiceDefinitions():
            if type == service_type:
                return interface

        raise NameError(service_type)
    getInterfaceFor = ContextMethod(getInterfaceFor)

    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.Services.ServiceManager.IComponentManager.

    def queryComponent(wrapped_self, type=None, filter=None, all=0):
        Packages = ContextWrapper(wrapped_self.Packages, wrapped_self,
                                  name='Packages')
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

    def get(wrapped_self, key, default=None):
        "See Interface.Common.Mapping.IReadMapping"

        if key == 'Packages':
            return wrapped_self.Packages

        directives = wrapped_self.queryConfigurations(key)
        if directives and directives[0] is not None:
            return wrapped_self.queryService(key, default)

        return default
    get = ContextMethod(get)

    def __contains__(self, key):
        "See Interface.Common.Mapping.IReadMapping"

        return self.get(key) is not None

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

        names=name.split('.')
        last=names[-1]
        mod='.'.join(names[:-1])

        if not mod:
            return wrapped_self.__import(name)

        while 1:
            m = wrapped_self.__import(mod)
            try:
                a=getattr(m, last)
            except AttributeError:
                if not repeat:
                    return wrapped_self.__import(name)

            else:
                if not repeat or (not isinstance(a, ModuleType)):
                    return a
            mod += '.' + last
    resolve = ContextMethod(resolve)

