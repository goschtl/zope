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
"""
$Id: ServiceConfiguration.py,v 1.3 2002/12/03 18:16:58 efge Exp $
"""

__metaclass__ = type

from Persistence import Persistent
from Zope.Security.Checker import CheckerPublic, InterfaceChecker
from Zope.Security.Proxy import Proxy
from Zope.App.DependencyFramework.Exceptions import DependencyError
from Zope.App.Traversing import traverse
from IServiceConfiguration import IServiceConfiguration
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.App.Traversing import getPhysicalRoot
from Zope.ComponentArchitecture import getService, getServiceManager
from Zope.App.Traversing import getPhysicalPathString
from ServiceManager import ServiceManager
from Zope.App.OFS.Container.IAddNotifiable import IAddNotifiable
from Zope.App.OFS.Container.IDeleteNotifiable import IDeleteNotifiable
from Zope.App.DependencyFramework.IDependable import IDependable
from Zope.ComponentArchitecture import getServiceManager, getAdapter
from Zope.ContextWrapper import ContextMethod
from Zope.App.OFS.Services.Configuration import ConfigurationStatusProperty
from Zope.ContextWrapper import ContextProperty
from IBindingAware import IBindingAware
from Zope.App.OFS.Services.ConfigurationInterfaces import Active
from Zope.App.OFS.Services.ConfigurationInterfaces import Registered
from Zope.App.OFS.Services.ConfigurationInterfaces import Unregistered

class ServiceConfiguration(Persistent):
    __doc__ = IServiceConfiguration.__doc__
    
    __implements__ = IServiceConfiguration, IAddNotifiable, IDeleteNotifiable

    status = ConfigurationStatusProperty('Services')

    def __init__(self, service_type, component_path, permission=None):
        self.serviceType = service_type
        self.componentPath = component_path
        if permission == 'Zope.Public':
            permission = CheckerPublic
            
        self.permission = permission

    def __repr__(self):
        return "service(%s, %s)" % (self.serviceType, self.componentPath)

    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.Services.ServiceManager.IServiceConfiguration.

    def getService(self):
        service_manager = getServiceManager(self)
        
        service = getattr(self, '_v_service', None)
        if service is None:
            
            # We have to be clever here. We need to do an honest to
            # god unrestricted traveral, which means we have to
            # traverse from an unproxies object. But, it's not enough
            # for the service manager to be unproxies, because the
            # path is an absolute path. When absolute paths are
            # traversed, the traverser finds the physical root and
            # traverses from there, so we need to make sure the
            # physical root isn;t proxied.

            # get the root and unproxy it.
            root = removeAllProxies(getPhysicalRoot(service_manager))            
            service = traverse(root, self.componentPath)

            if self.permission:
                if type(service) is Proxy:
                    # XXX what is this?
                    service = removeSecurityProxy(service)

                interface = service_manager.getInterfaceFor(self.serviceType)

                checker = InterfaceChecker(interface, self.permission)

                service = Proxy(service, checker)

            
            self._v_service = service


        return service

    getService.__doc__ = IServiceConfiguration['getService'].__doc__

    getService = ContextMethod(getService)

    ############################################################

    def activated(self):
        service = self.getService()
        if IBindingAware.isImplementedBy(service):
            service.bound(self.serviceType)

    activated = ContextMethod(activated)

    def deactivated(self):
        service = self.getService()
        if IBindingAware.isImplementedBy(service):
            service.unbound(self.serviceType)

    deactivated = ContextMethod(deactivated)

    def manage_afterAdd(self, configuration, container):
        "See Zope.App.OFS.Container.IAddNotifiable"
        sm = getServiceManager(configuration)
        service = configuration.getService()
        dependents = getAdapter(service, IDependable)
        objectpath = getPhysicalPathString(configuration)
        dependents.addDependent(objectpath)
        
    def manage_beforeDelete(self, configuration, container):
        "See Zope.App.OFS.Container.IDeleteNotifiable"
        assert self == configuration
        sm = getServiceManager(self)
        service = self.getService()
        objectstatus = self.status
        dependents = getAdapter(service, IDependable)
        objectpath = getPhysicalPathString(self)
        
        if objectstatus == Active:
            raise DependencyError("Can't delete active configurations")
        elif objectstatus == Registered:
            self.status = Unregistered

        dependents.removeDependent(objectpath)

    manage_beforeDelete = ContextMethod(manage_beforeDelete)
    
__doc__ = ServiceConfiguration.__doc__  + __doc__

            
