##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
import unittest

from zope.component.exceptions import ComponentLookupError
from zope.interface import Interface
from zope.interface.verify import verifyObject

from zope.app.component.globalinterfaceservice \
     import interfaceService as globalService
from zope.app.interfaces.component import IInterfaceService
from zope.app.services.interface import LocalInterfaceService
from zope.app.services.servicenames import Interfaces
from zope.app.tests import setup

from zope.app.component.tests.absIInterfaceService \
     import IInterfaceServiceTests

class Test(IInterfaceServiceTests, unittest.TestCase):
    """Test Interface for LocalInterfaceService instance."""

    def setUp(self):
        setup.placefulSetUp()

    def tearDown(self):
        setup.placefulTearDown()
        
    def getServices(self):
        rootFolder = setup.buildSampleFolderTree()
        mgr = setup.createServiceManager(rootFolder)
        service = setup.addService(mgr, Interfaces, LocalInterfaceService())
        return service, globalService

def test_suite():
    return unittest.makeSuite(Test)
