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
$Id: EventSetup.py,v 1.6 2002/11/30 18:37:17 jim Exp $
"""

from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
  import PlacefulSetup

from Zope.App.OFS.Services.ServiceManager.ServiceManager \
     import ServiceManager

from Zope.App.OFS.Services.LocalEventService.LocalEventService \
     import LocalEventService

from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration

from Zope.App.Traversing import getPhysicalPathString, traverse

from Zope.App.OFS.Services.ConfigurationInterfaces import Active

class EventSetup(PlacefulSetup):
    
    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.createEventService()

    def createServiceManager(self, folder):
        folder.setServiceManager(ServiceManager())

    def createEventService(self, path=None):

        folder = self.rootFolder
        if path is not None:
            folder = traverse(folder, path)

        if not folder.hasServiceManager():
            self.createServiceManager(folder)

        sm = traverse(folder, '++etc++Services')
        default = traverse(sm, 'Packages/default')
        default.setObject("myEventService", LocalEventService())

        path = "%s/Packages/default/myEventService" % getPhysicalPathString(sm)
        configuration = ServiceConfiguration("Events", path)
        default['configure'].setObject("myEventServiceDir", configuration)
        traverse(default, 'configure/1').status = Active
