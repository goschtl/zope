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
$Id: eventsetup.py,v 1.7 2003/05/01 19:35:35 faassen Exp $
"""
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.service import ServiceManager

class EventSetup(PlacefulSetup):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.createStandardServices()

    def createServiceManager(self, folder):
        folder.setServiceManager(ServiceManager())

