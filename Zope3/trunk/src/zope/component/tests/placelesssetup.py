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

$Id: placelesssetup.py,v 1.7 2003/11/21 17:09:32 jim Exp $
"""

# A mix-in class inheriting from CleanUp that also connects the CA services

from zope.testing.cleanup import CleanUp
from zope.component import getServiceManager
from zope.component.servicenames import Adapters, Utilities
from zope.component.servicenames import Factories, Presentation

class PlacelessSetup(CleanUp):
    def setUp(self):
        CleanUp.setUp(self)
        sm = getServiceManager(None)
        defineService = sm.defineService
        provideService = sm.provideService

        # factory service
        from zope.component.interfaces import IFactoryService
        defineService(Factories, IFactoryService)
        from zope.component.factory import factoryService
        provideService(Factories, factoryService)

        # utility service
        from zope.component.interfaces import IUtilityService
        defineService(Utilities, IUtilityService)
        from zope.component.utility import utilityService
        provideService(Utilities, utilityService)

        # adapter service
        from zope.component.interfaces import IAdapterService
        defineService(Adapters, IAdapterService)
        from zope.component.adapter import GlobalAdapterService
        provideService(Adapters, GlobalAdapterService())
        
        # presentation service
        from zope.component.interfaces import IPresentationService
        defineService(Presentation, IPresentationService)
        from zope.component.presentation import GlobalPresentationService
        provideService(Presentation, GlobalPresentationService())

    def tearDown(self):
        CleanUp.tearDown(self)
