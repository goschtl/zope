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
$Id: ObjectHubSetup.py,v 1.4 2002/12/11 09:04:08 mgedmin Exp $
"""

from Zope.App.OFS.Services.LocalEventService.tests.EventSetup import \
     EventSetup
from Zope.ComponentArchitecture import getServiceManager
from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration
from Zope.App.Traversing import getPhysicalPathString, traverse

from Zope.App.OFS.Services.ObjectHub.ObjectHub import ObjectHub
from Zope.App.OFS.Services.ConfigurationInterfaces import Active

class ObjectHubSetup(EventSetup):
    
    def setUp(self):
        EventSetup.setUp(self)
        
        from Zope.App.OFS.Services.ObjectHub.IObjectHub import IObjectHub
        global_service_manager = getServiceManager(None)
        global_service_manager.defineService("ObjectHub", IObjectHub)
        self.createObjectHub()
    
    def createObjectHub(self, path=None):
        folder = self.rootFolder
        if path is not None:
            folder = traverse(folder, path)

        if not folder.hasServiceManager():
            self.createServiceManager(folder)

        sm = traverse(folder, '++etc++Services')
        default = traverse(sm, 'Packages/default')
        default.setObject("myObjectHub", ObjectHub())

        path = "%s/Packages/default/myObjectHub" % getPhysicalPathString(sm)
        configuration = ServiceConfiguration("ObjectHub", path)

        configure = traverse(default, 'configure')
        key = configure.setObject("myObjectHubDir", configuration)
        traverse(configure, key).status = Active
