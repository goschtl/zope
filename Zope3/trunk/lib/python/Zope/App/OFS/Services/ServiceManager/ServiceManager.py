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

$Id: ServiceManager.py,v 1.4 2002/07/11 18:21:32 jim Exp $
"""
from Persistence import Persistent

from Zope.Exceptions import NotFoundError, ZopeError

from Zope.ComponentArchitecture.IServiceManagerContainer \
     import IServiceManagerContainer
from Zope.ComponentArchitecture \
     import getService, getNextServiceManager, getNextService
from Zope.ComponentArchitecture.GlobalServiceManager import UndefinedService
from Zope.ComponentArchitecture.GlobalServiceManager import InvalidService
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError

from Zope.App.OFS.Container.IContainer import ISimpleReadContainer
from Zope.App.OFS.Content.Folder.Folder import Folder
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.App.OFS.Container.BTreeContainer import BTreeContainer
from Zope.Proxy.ProxyIntrospection import removeAllProxies

from IBindingAware import IBindingAware
from Packages import Packages
from Package import Package
from IServiceManager import IServiceManager

class ServiceManager(Persistent):

    __implements__ = IServiceManager, ISimpleReadContainer

    def __init__(self):

        self.__bindings = {}
        # Bindings is of the form:
        #
        # {service_type -> [directives]}
        #
        # Where the first directive is always the active directive.

        self.Packages = Packages()
        self.Packages.setObject('default', Package())


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
        
        service = self.__bindings.get(name)

        if service:
            service = service[0] # Get the active service directive
            if service is not None: # not disabled
                service = service.getService(self) # get the service
                return service

        return getNextService(self, name)

    getService = ContextMethod(getService)


    def getBoundService(self, name):
        "See Zope.App.OFS.Services.ServiceManager.IServiceManager."

        service = self.__bindings.get(name)
        if service:
            service = service[0] # Get the active service directive
            service = service.getService(self) # get the service
            return service

        return None

    def getInterfaceFor(self, service_type):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        for type, interface in self.getServiceDefinitions():
            if type == service_type:
                return interface

        raise NameError(service_type)

    getInterfaceFor = ContextMethod(getInterfaceFor)

    def disableService(self, service_type):
        "See Zope.App.OFS.Services.ServiceManager.IServiceManager."
        directives = self.__bindings.get(service_type)
        if directives and directives[0] is not None:
            directives.insert(0, None)            

    def enableService(self, service_type, index):
        "See Zope.App.OFS.Services.ServiceManager.IServiceManager."
        self._disableFirstBeforeEnable(service_type)

        directives = self.__bindings.get(service_type)
        directive = directives[index]
        del directives[index]
        directives.insert(0, directive)


        self._p_changed = 1
                
        service = directive.getService(self)
        if IBindingAware.isImplementedBy(service):
            service.bound(service_type)


    def _disableFirstBeforeEnable(self, service_type):
        # Disable the first (active) service or remove the
        # disabled marker prior to enabling a service.
        directives = self.__bindings.get(service_type)

        if directives:
            if directives[0] is None:
                # remove deactivation marker
                del directives[0]
            elif IBindingAware.isImplementedBy(directives[0]):
                # unbind old service, if necessary
                old_service = directives[0].getService(self)
                old_service.unbound(service_type)
        

    def bindService(self, directive):
        "See "
        "Zope.App.OFS.Services.ServiceManager.IServiceManager.IServiceManager"
        service = directive.getService(self)
        service_type = directive.service_type

        interface = self.getInterfaceFor(service_type)
        
        if not interface.isImplementedBy(service):
            raise InvalidService(service_type, directive, interface)

        self._disableFirstBeforeEnable(service_type)

        bindings = self.__bindings
        if service_type not in bindings:
            bindings[service_type] = [directive]
        else:
            directives = bindings[service_type]
            directives.insert(0, directive)

        self._p_changed = 1
                
        if IBindingAware.isImplementedBy(service):
            service.bound(service_type)

    bindService = ContextMethod(bindService)

    def addService(self, directive):
        "See "
        "Zope.App.OFS.Services.ServiceManager.IServiceManager.IServiceManager"
        service = directive.getService(self)
        service_type = directive.service_type

        interface = self.getInterfaceFor(service_type)
        
        if not interface.isImplementedBy(service):
            raise InvalidService(service_type, directive, interface)

        bindings = self.__bindings
        if service_type not in bindings:
            bindings[service_type] = []
        bindings[service_type].append(directive)

        self._p_changed = 1
                
        if len(bindings) == 1 and IBindingAware.isImplementedBy(service):
            service.bound(service_type)

    addService = ContextMethod(addService)
    
    def unbindService(self, directive):
        "See Zope.App.OFS.Services.ServiceManager.IServiceManager.IServiceManager"
        self = removeAllProxies(self)
        service = directive.getService(self)        
        service_type = directive.service_type

        directives = self.__bindings[service_type]
        if directive not in directives:
            raise KeyError(directive)
        
        if IBindingAware.isImplementedBy(service):
            service.unbound(service_type)


        self.__bindings[service_type] = [d for d in directives
                                         if d != directive]

        self._p_changed = 1
    
    unbindService = ContextMethod(unbindService)

    def getDirectives(self, service_type):
        "See "
        "Zope.App.OFS.Services.ServiceManager.IServiceManager.IServiceManager"
        return self.__bindings[service_type]

    def getBoundServiceTypes(self):
        "See Zope.App.OFS.Services.ServiceManager.IServiceManager.IServiceManager"
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

        return self.queryService(key, default)

    def __contains__(self, key):
        "See Interface.Common.Mapping.IReadMapping"

        return self.get(key) is not None

