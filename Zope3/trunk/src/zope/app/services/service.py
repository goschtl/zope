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

Revision information:
$Id: service.py,v 1.2 2002/12/25 14:13:19 jim Exp $
"""

from zope.app.interfaces.services.service import IServiceManagerContainer
from zope.component.interfaces import IServiceService
from zope.component.exceptions import ComponentLookupError

_marker = object()

class ServiceManagerContainer:

    __implements__ =  IServiceManagerContainer

    def hasServiceManager(self):
        '''See interface IReadServiceManagerContainer'''
        return hasattr(self, '_ServiceManagerContainer__sm')

    def getServiceManager(self):
        '''See interface IReadServiceManagerContainer'''

        try:
            return self.__sm
        except AttributeError:
            raise ComponentLookupError('no service manager defined')

    def queryServiceManager(self, default=None):
        '''See interface IReadServiceManagerContainer'''

        return getattr(self, '_ServiceManagerContainer__sm', default)

    def setServiceManager(self, sm):
        '''See interface IWriteServiceManagerContainer'''

        if IServiceService.isImplementedBy(sm):
            self.__sm = sm
        else:
            raise ValueError('setServiceManager requires an IServiceService')

    #
    ############################################################



"""
$Id: service.py,v 1.2 2002/12/25 14:13:19 jim Exp $
"""

from zope.app.interfaces.services.service import IServiceConfiguration
from zope.app.interfaces.services.service import IBindingAware
from zope.app.services.configuration import ConfigurationStatusProperty
from zope.app.services.configuration import NamedComponentConfiguration
from zope.proxy.context import ContextMethod
from zope.component import getServiceManager

class ServiceConfiguration(NamedComponentConfiguration):

    __doc__ = IServiceConfiguration.__doc__

    __implements__ = (IServiceConfiguration,
                      NamedComponentConfiguration.__implements__)

    status = ConfigurationStatusProperty('Services')

    label = "Service"

    def __init__(self, *args, **kw):
        super(ServiceConfiguration, self).__init__(*args, **kw)

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

__doc__ = ServiceConfiguration.__doc__  + __doc__




"""XXX I need a summary line.

In addition, a ServiceManager acts as a registry for persistent
modules.  The Zope import hook uses the ServiceManager to search for
modules.

$Id: service.py,v 1.2 2002/12/25 14:13:19 jim Exp $
"""

import sys

from zope.app.component.nextservice \
     import getNextServiceManager, getNextService
from zope.component.exceptions import ComponentLookupError

from zope.app.interfaces.container import ISimpleReadContainer
from zope.proxy.context import ContextMethod
from zope.proxy.context import ContextWrapper
from zope.proxy.introspection import removeAllProxies

from zope.app.services.package import Packages
from zope.app.interfaces.services.service import IServiceManager

from zope.app.services.configuration import NameComponentConfigurable

from zodb.code.module import PersistentModuleRegistry
from zodb.code.module import PersistentModule
from zope.app.interfaces.services.service import INameResolver

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

    def queryComponent(wrapped_self, type=None, filter=None, all=0):
        Packages = ContextWrapper(wrapped_self.Packages, wrapped_self,
                                  name='Packages')
        return Packages.queryComponent(type, filter, all)
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

        service = wrapped_self.queryActiveComponent(key)
        if service is None:
            return default

        return service

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
