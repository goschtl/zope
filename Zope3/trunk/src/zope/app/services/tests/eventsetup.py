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
$Id: eventsetup.py,v 1.2 2002/12/25 14:13:20 jim Exp $
"""

from zope.app.services.tests.placefulsetup \
  import PlacefulSetup

from zope.app.services.service \
     import ServiceManager

from zope.app.services.event \
     import LocalEventService

from zope.app.services.service \
     import ServiceConfiguration

from zope.app.traversing import getPhysicalPathString, traverse

from zope.app.interfaces.services.configuration import Active

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
