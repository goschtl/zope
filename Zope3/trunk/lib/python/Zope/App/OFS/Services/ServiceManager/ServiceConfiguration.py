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
$Id: ServiceConfiguration.py,v 1.5 2002/12/12 11:32:32 mgedmin Exp $
"""

from IServiceConfiguration import IServiceConfiguration
from IBindingAware import IBindingAware
from Zope.App.OFS.Services.Configuration import ConfigurationStatusProperty
from Zope.App.OFS.Services.Configuration import NamedComponentConfiguration
from Zope.ContextWrapper import ContextMethod
from Zope.ComponentArchitecture import getServiceManager

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


