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
$Id: objecthubsetup.py,v 1.2 2002/12/25 14:13:20 jim Exp $
"""

from zope.app.services.tests.eventsetup import EventSetup
from zope.component import getServiceManager
from zope.app.services.service import ServiceConfiguration
from zope.app.traversing import getPhysicalPathString, traverse

from zope.app.services.hub import ObjectHub
from zope.app.interfaces.services.configuration import Active

class ObjectHubSetup(EventSetup):

    def setUp(self):
        EventSetup.setUp(self)

        from zope.app.interfaces.services.hub import IObjectHub
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
