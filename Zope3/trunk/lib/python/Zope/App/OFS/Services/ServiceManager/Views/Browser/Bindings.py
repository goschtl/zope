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

$Id: Bindings.py,v 1.2 2002/06/10 23:28:13 jim Exp $
"""

from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture.ContextDependent import ContextDependent
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError
from Zope.Proxy.ProxyIntrospection import removeAllProxies

class Bindings(BrowserView):

    index = ViewPageTemplateFile('services_bindings.pt')

    def getServicesTable(self):
        """
        """
        context = self.context
        allServices = removeAllProxies(context.getServiceDefinitions())
        localServices = removeAllProxies(context.items())
        services = []
        for serviceName, service in allServices:
            serviceMap={}
            availableServices = []

            acquiredOrNone = 'None'
            bound = context.getBoundService(serviceName)
            
            if bound is None:
                try:
                    acquired = context.getService(serviceName)
                    acquiredOrNone = 'Acquired'
                except ComponentLookupError:
                    pass
                bound = acquiredOrNone
                                
            availableServices.append(acquiredOrNone)

            
            for localServiceName, localService in localServices:
                if service.isImplementedBy(localService):
                    availableServices.append(localServiceName)

            serviceMap['name'] = serviceName
            serviceMap['services'] = availableServices
            serviceMap['bound'] = bound
            services.append(serviceMap)
        return services
    
    def action(self, boundService, REQUEST):
        # boundService is a dict service_name:bound_name
        # the bound_names Acquired and None are special
        
        context = self.context
        
        change_count = 0
        
        for service_name, new_bound_name in boundService.items():
            # check to see if the bound name has changed
            current_bound_name = context.getBoundService(service_name)
            if new_bound_name in ('Acquired', 'None'):
                new_bound_name = None
            if current_bound_name != new_bound_name:
                change_count += 1

                if new_bound_name is None:
                    context.unbindService(service_name)
                else:
                    context.bindService(service_name, new_bound_name)
        if change_count:
            message = "bindings changed"
        else:
            message = "no bindings changed"
        return self.index(REQUEST=REQUEST, message=message)
    
