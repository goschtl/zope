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

Revision information:
$Id: placelesssetup.py,v 1.3 2003/02/06 06:50:08 seanb Exp $
"""

# A mix-in class inheriting from CleanUp that also connects the CA services

from zope.testing.cleanup import CleanUp
from zope.component import getServiceManager
from zope.component.servicenames import Adapters, Skins, Utilities
from zope.component.servicenames import ResourceService, Factories

class PlacelessSetup(CleanUp):
    def setUp(self):
        CleanUp.setUp(self)
        sm=getServiceManager(None)
        defineService=sm.defineService
        provideService=sm.provideService
        # factory service
        from zope.component.interfaces import IFactoryService
        defineService(Factories,IFactoryService)
        from zope.component.factory import factoryService
        provideService(Factories, factoryService)
        # utility service
        from zope.component.interfaces import IUtilityService
        defineService(Utilities,IUtilityService)
        from zope.component.utility import utilityService
        provideService(Utilities, utilityService)
        # adapter service
        from zope.component.interfaces import IAdapterService
        defineService(Adapters,IAdapterService)
        from zope.component.adapter import adapterService
        provideService(Adapters, adapterService)
        # resource service
        from zope.component.interfaces import IResourceService
        defineService(ResourceService,IResourceService)
        from zope.component.resource import resourceService
        provideService(ResourceService, resourceService)
        # skin service
        from zope.component.interfaces import ISkinService
        defineService(Skins,ISkinService)
        from zope.component.skin import skinService
        provideService(Skins, skinService)
        # view service
        from zope.component.interfaces import IViewService
        defineService('Views',IViewService)
        from zope.component.view import viewService
        provideService('Views', viewService)
    def tearDown(self):
        CleanUp.tearDown(self)
