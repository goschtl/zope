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
$Id: TestingServiceManager.py,v 1.3 2002/12/09 15:23:28 ryzaja Exp $
"""

__metaclass__ = type

from Zope.ComponentArchitecture.IServiceService import IServiceService
from Zope.App.ComponentArchitecture.NextService \
     import getNextService, getNextServiceManager
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.App.OFS.Services.ServiceManager.IBindingAware import IBindingAware
from Zope.ContextWrapper import ContextMethod

class TestingServiceManager:
    """Simple placeful service manager used for writing tests
    """
    __implements__ =  IServiceService

    def getServiceDefinitions(self):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        return getNextServiceManager(self).getServiceDefinitions()

    def getInterfaceFor(self, name):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        return getNextServiceManager(self).getInterfaceFor(name)

    def getService(self, name):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        if hasattr(self, name):
            return ContextWrapper(getattr(self, name), self, name=name)
        return getNextServiceManager(self).getService(name)

    getService = ContextMethod(getService)

    def queryService(self, name, default=None):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        if hasattr(self, name):
            return ContextWrapper(getattr(self, name), self, name=name)
        return getNextServiceManager(self).queryService(name, default)

    queryService = ContextMethod(queryService)

    def bindService(self, name, ob):
        setattr(self, name, ob)
        if IBindingAware.isImplementedBy(ob):
            ob.bound(name)

    bindService = ContextMethod(bindService)

    def unbindService(self, name):
        ob = getattr(self, name)
        if IBindingAware.isImplementedBy(ob):
            ob.unbound(name)
        delattr(self, name, ob)

    unbindService = ContextMethod(unbindService)


__doc__ = TestingServiceManager.__doc__ + __doc__

