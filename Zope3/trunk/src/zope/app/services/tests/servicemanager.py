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
$Id: servicemanager.py,v 1.3 2003/05/01 19:35:35 faassen Exp $
"""

__metaclass__ = type

from zope.component.interfaces import IServiceService
from zope.app.component.nextservice import getNextServiceManager
from zope.proxy.context import ContextWrapper
from zope.app.interfaces.services.service import IBindingAware
from zope.proxy.context import ContextMethod

class TestingServiceManager:
    """Simple placeful service manager used for writing tests
    """
    __implements__ =  IServiceService

    def getServiceDefinitions(self):
        "See IServiceService"
        return getNextServiceManager(self).getServiceDefinitions()

    def getInterfaceFor(self, name):
        "See IServiceService"
        return getNextServiceManager(self).getInterfaceFor(name)

    def getService(self, name):
        "See IServiceService"
        if hasattr(self, name):
            return ContextWrapper(getattr(self, name), self, name=name)
        return getNextServiceManager(self).getService(name)

    getService = ContextMethod(getService)

    def queryService(self, name, default=None):
        "See IServiceService"
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
