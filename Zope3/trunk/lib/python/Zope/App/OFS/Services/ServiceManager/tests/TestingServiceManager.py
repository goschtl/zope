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
$Id: TestingServiceManager.py,v 1.1 2002/11/13 20:34:03 gvanrossum Exp $
"""

__metaclass__ = type

from Zope.ComponentArchitecture.IServiceService import IServiceService
from Zope.App.ComponentArchitecture.NextService \
     import getNextService, getNextServiceManager
from Zope.Proxy.ContextWrapper import ContextWrapper

class TestingServiceManager:
    """Simple placeful service manager used for writing tests
    """
    __implements__ =  IServiceService


    def getServiceDefinitions(self):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        return getNextServiceManager.getServiceDefinitions()

    def getInterfaceFor(self, name):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        return getNextServiceManager.getServiceDefinitions()

    def getService(self, name):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        if hasattr(self, name):
            return ContextWrapper(getattr(self, name), self, name=name)
        return getNextServiceManager.getService(name)

    def queryService(self, name, default=None):
        "See Zope.ComponentArchitecture.IServiceService.IServiceService"
        if hasattr(self, name):
            return ContextWrapper(getattr(self, name), self, name=name)
        return getNextServiceManager.queryService(name, default)

__doc__ = TestingServiceManager.__doc__ + __doc__

