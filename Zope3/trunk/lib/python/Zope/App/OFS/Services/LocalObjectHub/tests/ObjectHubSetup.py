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
$Id: ObjectHubSetup.py,v 1.1 2002/10/21 06:14:47 poster Exp $
"""


from Zope.App.OFS.Services.LocalEventService.tests.EventSetup import \
     EventSetup
from Zope.ComponentArchitecture import getService, getServiceManager
from Zope.App.OFS.Services.ServiceManager.ServiceDirective \
     import ServiceDirective
from Zope.App.Traversing import getPhysicalPathString

from Zope.App.OFS.Services.LocalObjectHub.LocalObjectHub import LocalObjectHub

class ObjectHubSetup(EventSetup):
    
    def setUp(self):
        EventSetup.setUp(self)
        
        from Zope.ObjectHub.IObjectHub import IObjectHub
        globsm=getServiceManager(None)
        globsm.defineService("ObjectHub", IObjectHub)
        self.createObjectHub()
    
    def createObjectHub(self, folder=None):
        if folder is None: folder=self.rootFolder
        if not folder.hasServiceManager():
            self.createServiceManager(folder)
        sm=getServiceManager(folder) # wrapped now
        sm.Packages['default'].setObject("myObjectHub",LocalObjectHub())

        path = "%s/Packages/default/myObjectHub" % getPhysicalPathString(sm)
        directive = ServiceDirective("ObjectHub", path)
        sm.Packages['default'].setObject("myObjectHubDir", directive)
        sm.bindService(directive)