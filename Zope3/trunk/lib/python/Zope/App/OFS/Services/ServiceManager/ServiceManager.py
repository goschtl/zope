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

$Id: ServiceManager.py,v 1.2 2002/06/10 23:28:12 jim Exp $
"""

from IServiceManager import IServiceManager
from Zope.ComponentArchitecture.IServiceManagerContainer \
     import IServiceManagerContainer
from Zope.ComponentArchitecture import getService, \
     getNextServiceManager, getNextService
from Zope.ComponentArchitecture.GlobalServiceManager import UndefinedService
from Zope.ComponentArchitecture.GlobalServiceManager import InvalidService
from Zope.Exceptions import NotFoundError, ZopeError
from Zope.App.OFS.Content.Folder.Folder import Folder
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.App.OFS.Container.BTreeContainer import BTreeContainer
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from IBindingAware import IBindingAware

class ServiceManager(BTreeContainer):

    __implements__ = IServiceManager

    def __init__(self):
        self.__bindings = {}
        super(ServiceManager, self).__init__()


    def getServiceDefinitions(wrapped_self):
        clean_self=removeAllProxies(wrapped_self)
        """ see IServiceManager Interface """
        # Get the services defined here and above us, if any (as held
        # in a ServiceInterfaceService, presumably)
        sm=getNextServiceManager(wrapped_self)
        if sm is not None:
            serviceDefs=sm.getServiceDefinitions()
        else: serviceDefs={}
        # since there is no way to define an interface TTW right now,
        # worrying about this further is pointless--it probably will be
        # an interface service evetually though...so this would be useful then:

        serviceInterfaceServ= \
             clean_self.__bindings.get('ServiceInterfaceService')
        if serviceInterfaceServ:
            serviceDefs.update(dict(
               removeAllProxies(
                   wrapped_self[serviceInterfaceServ].items()
                   )
               ))
        return serviceDefs

    getServiceDefinitions=ContextMethod(getServiceDefinitions)

    def getService(wrapped_self, name):
        """ see IServiceManager Interface"""
        clean_self=removeAllProxies(wrapped_self)

        service = clean_self.__bindings.get(name)

        if service:
            return ContextWrapper(wrapped_self[service],
                                  wrapped_self, name=service) # we want
        # to traverse by component name, not service name

        return getNextService(wrapped_self, name)

    getService=ContextMethod(getService)

    def getBoundService(self, name):
        """ see IServiceManager Interface"""

        return self.__bindings.get(name)

    def bindService(wrapped_self, serviceName, serviceComponentName):
        """ see IServiceManager Interface"""
        clean_self=removeAllProxies(wrapped_self)

        # This could raise a KeyError if we don't have this component
        clean_serviceComponent = wrapped_self[serviceComponentName]
        wrapped_serviceComponent=ContextWrapper(
            clean_serviceComponent,
            wrapped_self,
            name=serviceComponentName)

        for name,interface in wrapped_self.getServiceDefinitions():
            if name == serviceName:
                if not interface.isImplementedBy(clean_serviceComponent):
                    raise InvalidService(serviceName,
                                         serviceComponentName,
                                         interface)
            break

        # Services are added to the Manager through the Folder interface
        # self.setObject(name, component)
        
        if IBindingAware.isImplementedBy(clean_serviceComponent):
            wrapped_serviceComponent.bound(serviceName)

        clean_self.__bindings[serviceName] = serviceComponentName

        # trigger persistence
        clean_self.__bindings = clean_self.__bindings

    bindService=ContextMethod(bindService) # needed because of call to
    # getServiceDefinitions, as well as IBindingAware stuff

    def unbindService(wrapped_self, serviceName):
        """ see IServiceManager Interface """
        clean_self=removeAllProxies(wrapped_self)
        serviceComponentName=clean_self.__bindings[serviceName]
        
        clean_serviceComponent = wrapped_self[serviceComponentName]
        wrapped_serviceComponent=ContextWrapper(
            clean_serviceComponent,
            wrapped_self,
            name=serviceComponentName)
        
        if IBindingAware.isImplementedBy(clean_serviceComponent):
            wrapped_serviceComponent.unbound(serviceName)

        del clean_self.__bindings[serviceName]

        # trigger persistence
        clean_self.__bindings = clean_self.__bindings
    
    unbindService=ContextMethod(unbindService)


    def __delitem__(self, name):
        '''See interface IWriteContainer'''
        if name in self.__bindings.values():
            # Should we silently unbind the service?
            # self.unbindService(name)
            # No, let's raise an exception
            raise ZopeError("Cannot remove a bound service. Unbind it first.")
        BTreeContainer.__delitem__(self, name)
