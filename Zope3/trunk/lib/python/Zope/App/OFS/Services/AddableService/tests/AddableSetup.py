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
$Id: AddableSetup.py,v 1.2 2002/06/10 23:28:10 jim Exp $
"""

from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup import PlacefulSetup

class AddableSetup(PlacefulSetup):
    
    def setUp(self):
        PlacefulSetup.setUp(self)
        from Zope.App.OFS.Services.AddableService.IAddableService import \
           IAddableService
        from Zope.ComponentArchitecture import getServiceManager
        sm=getServiceManager(None)
        defineService=sm.defineService
        provideService=sm.provideService
        defineService('AddableContent',IAddableService)
        defineService('AddableServices',IAddableService)
        from Zope.App.OFS.Services.AddableService.GlobalAddableService import \
           addableContent, addableServices
        provideService('AddableContent',addableContent)
        provideService('AddableServices',addableServices)

