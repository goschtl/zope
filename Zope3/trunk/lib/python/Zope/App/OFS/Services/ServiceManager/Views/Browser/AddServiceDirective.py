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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: AddServiceDirective.py,v 1.2 2002/11/18 13:26:36 stevea Exp $
"""
__metaclass__ = type

from Zope.ComponentArchitecture import getServiceManager
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.Services.ServiceManager.ServiceDirective \
     import ServiceDirective

class AddServiceDirective(BrowserView):

    def services(self):
        service = getServiceManager(self.context.context)
        definitions = service.getServiceDefinitions()
        return [name for (name, interface) in definitions]

    def components(self):
        service_type = self.request['service_type']
        service = getServiceManager(self.context.context)
        type = service.getInterfaceFor(service_type)
        return [info['path']
                for info in service.queryComponent(type=type)
                ]

    def action(self, service_type, component_path, status=""):
        sd = ServiceDirective(service_type, component_path)
        self.context.add(sd)
        service = getServiceManager(self.context.context)
        if status:
            if status == 'register':
                service.addService(sd)
            else:
                service.bindService(sd)
        self.request.response.redirect(self.context.nextURL())

