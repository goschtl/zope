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
$Id: testServiceManager.py,v 1.2 2002/06/10 23:28:13 jim Exp $
"""
from unittest import TestCase, TestLoader, TextTestRunner
from Zope.App.OFS.Container.tests.testIContainer import BaseTestIContainer

from Interface import Interface
from Zope.App.OFS.Content.Folder.RootFolder import RootFolder
from Zope.App.OFS.Content.Folder.Folder import Folder
from Zope.Proxy.ContextWrapper import getWrapperContext
from Zope.App.OFS.Services.ServiceManager.ServiceManager import ServiceManager
from Zope.ComponentArchitecture import getService, getServiceManager
from Zope.Exceptions import ZopeError
from PlacefulSetup import PlacefulSetup

class ITestService(Interface): pass

class TestService:

    __implements__ = ITestService

class ServiceManagerTests(PlacefulSetup, BaseTestIContainer, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()

    def _Test__new(self):
        return ServiceManager()

    def testAddService(self):
        sm = ServiceManager()
        self.rootFolder.setServiceManager(sm)
        sm=getServiceManager(self.rootFolder)
        ts = TestService()
        sm.setObject('test_service1', ts)
        self.assertEqual(sm['test_service1'], ts)

    def testGetService(self):
        sm = ServiceManager()
        self.rootFolder.setServiceManager(sm)
        sm=getServiceManager(self.rootFolder)
        ts = TestService()
        sm.setObject('test_service1', ts)
        sm.bindService('test_service', 'test_service1')
        testOb=getService(self.rootFolder, 'test_service')
        self.assertEqual(getWrapperContext
             (getWrapperContext(testOb)),self.rootFolder)
        self.assertEqual(testOb, ts)

    def testUnbindService(self):
        sm = ServiceManager()
        self.rootFolder.setServiceManager(sm)
        sm=getServiceManager(self.rootFolder)
        ts = TestService()
        root_ts = TestService()
        gsm=getServiceManager(None)
        gsm.defineService('test_service', ITestService)
        gsm.provideService('test_service', root_ts)

        sm.setObject('test_service1', ts)
        sm.bindService('test_service', 'test_service1')
        self.assertEqual(getService(self.rootFolder, 'test_service'), ts)
        sm.unbindService('test_service')
        self.assertEqual(getService(self.rootFolder, 'test_service'), root_ts)

    def testDeleteService(self):
        self.rootFolder.setServiceManager(ServiceManager())
        sm=getServiceManager(self.rootFolder)
        ts = TestService()
        
        sm.setObject('test_service1', ts)
        sm.bindService('test_service', 'test_service1')
        self.assertEqual(getService(self.rootFolder, 'test_service'), ts)
        self.assertRaises(ZopeError, sm.__delitem__, 'test_service1')
    
    def testContextServiceLookup(self):
        self.rootFolder.setServiceManager(ServiceManager())
        sm=getServiceManager(self.rootFolder)
        ts = TestService()
        sm.setObject('test_service1', ts)
        sm.bindService('test_service', 'test_service1')
        self.assertEqual(getService(self.folder1, 'test_service'), ts)
        self.assertEqual(getService(self.folder1_1, 'test_service'), ts)

    def testContextServiceLookupWithMultipleServiceManagers(self):
        self.rootFolder.setServiceManager(ServiceManager())
        sm=getServiceManager(self.rootFolder)
        ts = TestService()
        sm.setObject('test_service1', ts)
        sm.bindService('test_service', 'test_service1')

        self.folder1.setServiceManager(ServiceManager())
        sm2=getServiceManager(self.folder1)
        
        self.assertEqual(getService(self.folder1, 'test_service'), ts)

    def testComponentArchitectureServiceLookup(self):
        self.rootFolder.setServiceManager(ServiceManager())
        sm=getServiceManager(self.rootFolder)
        self.folder1.setServiceManager(ServiceManager())
        sm2=getServiceManager(self.folder1)
        
        ts = TestService()

        globsm=getServiceManager(None)
        globsm.defineService('test_service', ITestService)
        globsm.provideService('test_service', ts)

        service = getService(self.folder1, 'test_service')
        self.assertEqual(service, ts)


        
def test_suite():
    loader=TestLoader()
    return loader.loadTestsFromTestCase(ServiceManagerTests)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
