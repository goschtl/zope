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
$Id: ServiceConfiguration.py,v 1.4 2002/12/05 17:00:44 jim Exp $
"""

from IServiceConfiguration import IServiceConfiguration
from Zope.App.OFS.Services.Configuration import ConfigurationStatusProperty
from IBindingAware import IBindingAware
from Zope.App.OFS.Services.Configuration import ComponentConfiguration
from Zope.ContextWrapper import ContextMethod

class ServiceConfiguration(ComponentConfiguration):
    __doc__ = IServiceConfiguration.__doc__
    
    __implements__ = (IServiceConfiguration,
                      ComponentConfiguration.__implements__)

    status = ConfigurationStatusProperty('Services')

    def __init__(self, service_type, *args, **kw):
        self.serviceType = service_type
        super(ServiceConfiguration, self).__init__(*args, **kw)

    ############################################################

    def activated(self):
        service = self.getComponent()
        if IBindingAware.isImplementedBy(service):
            service.bound(self.serviceType)

    activated = ContextMethod(activated)

    def deactivated(self):
        service = self.getComponent()
        if IBindingAware.isImplementedBy(service):
            service.unbound(self.serviceType)

    deactivated = ContextMethod(deactivated)
    
__doc__ = ServiceConfiguration.__doc__  + __doc__

            
