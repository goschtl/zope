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
$Id: ObjectHubSetup.py,v 1.2 2002/11/26 19:02:49 stevea Exp $
"""

from Zope.App.OFS.Services.LocalEventService.tests.EventSetup import \
     EventSetup
from Zope.ComponentArchitecture import getServiceManager
from Zope.App.OFS.Services.ServiceManager.ServiceDirective \
     import ServiceDirective
from Zope.App.Traversing import getPhysicalPathString

from Zope.App.OFS.Services.ObjectHub.ObjectHub import ObjectHub

class ObjectHubSetup(EventSetup):
    
    def setUp(self):
        EventSetup.setUp(self)
        
        from Zope.App.OFS.Services.ObjectHub.IObjectHub import IObjectHub
        global_service_manager = getServiceManager(None)
        global_service_manager.defineService("ObjectHub", IObjectHub)
        self.createObjectHub()
    
    def createObjectHub(self, folder=None):
        if folder is None:
            folder = self.rootFolder
        if not folder.hasServiceManager():
            self.createServiceManager(folder)
        sm = getServiceManager(folder)  # wrapped now
        sm.Packages['default'].setObject("myObjectHub", ObjectHub())

        path = "%s/Packages/default/myObjectHub" % getPhysicalPathString(sm)
        directive = ServiceDirective("ObjectHub", path)
        sm.Packages['default'].setObject("myObjectHubDir", directive)
        sm.bindService(directive)

