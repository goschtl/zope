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

$Id: AddServiceConfiguration.py,v 1.2 2002/11/30 18:39:17 jim Exp $
"""
__metaclass__ = type

from Zope.ComponentArchitecture import getServiceManager
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration
from Zope.App.OFS.Services.ConfigurationInterfaces import IConfiguration
from Zope.App.Forms.Utility import setUpWidgets, getWidgetsDataForContent

class AddServiceConfiguration(BrowserView):

    def __init__(self, *args):
        super(AddServiceConfiguration, self).__init__(*args)
        setUpWidgets(self, IConfiguration)

    def services(self):
        service = getServiceManager(self.context.context)
        definitions = service.getServiceDefinitions()
        names = [name for (name, interface) in definitions]
        names.sort()
        return names

    def components(self):
        service_type = self.request['service_type']
        service = getServiceManager(self.context.context)
        type = service.getInterfaceFor(service_type)
        paths = [info['path']
                 for info in service.queryComponent(type=type)
                 ]
        paths.sort()
        return paths

    def action(self, service_type, component_path):
        sd = ServiceConfiguration(service_type, component_path)
        sd = self.context.add(sd)
        getWidgetsDataForContent(self, IConfiguration, sd)
        self.request.response.redirect(self.context.nextURL())

