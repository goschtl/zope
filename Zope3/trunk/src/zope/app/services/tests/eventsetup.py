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
$Id: eventsetup.py,v 1.4 2002/12/30 14:03:17 stevea Exp $
"""
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.service import ServiceManager, ServiceConfiguration
from zope.app.services.event import EventService
from zope.app.traversing import getPhysicalPathString, traverse
from zope.app.interfaces.services.configuration import Active
from zope.app.interfaces.services.event import ISubscriptionService

class EventSetup(PlacefulSetup):
    
    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.createStandardServices()

    def createServiceManager(self, folder):
        folder.setServiceManager(ServiceManager())

