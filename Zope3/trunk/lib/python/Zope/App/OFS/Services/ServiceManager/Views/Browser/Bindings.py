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

$Id: Bindings.py,v 1.3 2002/07/11 18:21:32 jim Exp $
"""

from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture import getView
from Zope.ComponentArchitecture.ContextDependent import ContextDependent
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError
from Zope.Proxy.ProxyIntrospection import removeAllProxies

class Bindings(BrowserView):

    index = ViewPageTemplateFile('services_bindings.pt')

    def getServicesTable(self):
        service_types = list(self.context.getBoundServiceTypes())
        service_types.sort()

        table = []

        for service_type in service_types:
            directives = self.context.getDirectives(service_type)

            if directives and directives[0] is None:
                active = None
                inactive = 1
            else:
                active = 1
                inactive = None

            directive_data = []
            for directive in directives:
                if directive is None:
                    continue

                service = directive.getService(self.context)
                service_url = str(
                    getView(service, 'absolute_url', self.request))
                sm_url = '/'.join(service_url.split('/')[:-2])

                component_path = directive.component_path
                l = component_path.find('/++etc++Services')
                sm_path = component_path[:l]
                componen_path = component_path[l+17:]

                directive_data.append({
                    'sm_url': sm_url,
                    'sm_path': sm_path,
                    'component_url': service_url,
                    'component_path': component_path,
                    })
                    
            
            table.append({
                'name': service_type,
                'directives': directive_data,
                'active': active,
                'inactive': inactive,
            })


        return table

    def _bound_status(self, service_type):
        directives = self.context.getDirectives(service_type)
        if directives and directives[0] is not None:
            return '0'
        return 'disabled'
            
    def action(self):
        if self.request.get('REQUEST_METHOD') != 'POST':
            return self.index()
        
        
        # Update the binding data based on informatioin in the request
        service_types = self.context.getBoundServiceTypes()
        change_count = 0

        for service_type in service_types:
            setting = self.request.get("service %s" % service_type)
            if setting is not None:
                current = self._bound_status(service_type)
                if current is not setting:
                    change_count += 1
                    if setting == 'disable':
                        self.context.disableService(service_type)
                    else:
                        self.context.enableService(service_type, int(setting))
                        
        if change_count:
            message = "%s bindings changed" % change_count
        else:
            message = "no bindings changed"

        return self.index(message=message)
    
