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
$Id: testServiceManager.py,v 1.6 2002/12/19 20:38:26 jim Exp $
"""
from unittest import TestCase, TestLoader, TextTestRunner

from Interface import Interface
from Zope.App.OFS.Content.Folder.RootFolder import RootFolder
from Zope.App.OFS.Content.Folder.Folder import Folder
from Zope.Proxy.ContextWrapper import getWrapperContext, getWrapperContainer
from Zope.App.OFS.Services.ServiceManager.ServiceManager import ServiceManager
from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration
from Zope.ComponentArchitecture import getService, getServiceManager
from Zope.Exceptions import ZopeError
from PlacefulSetup import PlacefulSetup
from Zope.App.Traversing import traverse
from Zope.App.OFS.Services.ConfigurationInterfaces \
     import Active, Unregistered, Registered
from Zope.ComponentArchitecture.GlobalServiceManager \
     import serviceManager

class ITestService(Interface):
    pass

class TestService:

    __implements__ = ITestService

class ServiceManagerTests(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()

        serviceManager.defineService('test_service', ITestService)

    def _Test__new(self):
        return ServiceManager()

    def createServiceManager(self):
        self.rootFolder.setServiceManager(ServiceManager())

    def testGetService(self):
        self.createServiceManager()
        sm = traverse(self.rootFolder, '++etc++Services')
        default = traverse(sm, 'Packages/default')

        ts = TestService()
        default.setObject('test_service1', ts)
        configuration = ServiceConfiguration(
            'test_service',
            '/++etc++Services/Packages/default/test_service1')

        default['configure'].setObject('', configuration)
        traverse(default, 'configure/1').status = Active

        testOb = getService(self.rootFolder, 'test_service')
        c = getWrapperContainer
        self.assertEqual(c(c(c(c(testOb)))), self.rootFolder)
        self.assertEqual(testOb, ts)

    def test_get(self):
        self.createServiceManager()
        sm = traverse(self.rootFolder, '++etc++Services')
        default = traverse(sm, 'Packages/default')
        
        ts = TestService()
        default.setObject('test_service1', ts)
        configuration = ServiceConfiguration(
            'test_service',
            '/++etc++Services/Packages/default/test_service1')

        default['configure'].setObject('', configuration)
        traverse(default, 'configure/1').status = Active

        testOb = sm.get('test_service')
        self.assertEqual(testOb, ts)
        testOb = sm.get('test_service2')
        self.assertEqual(testOb, None)

    def testAddService(self):
        self.createServiceManager()
        sm = traverse(self.rootFolder, '++etc++Services')
        default = traverse(sm, 'Packages/default')

        ts1 = TestService()
        default.setObject('test_service1', ts1)
        configuration = ServiceConfiguration(
            'test_service',
            '/++etc++Services/Packages/default/test_service1')
        default['configure'].setObject('', configuration)
        traverse(default, 'configure/1').status = Active

        ts2 = TestService()
        default.setObject('test_service2', ts2)
        configuration = ServiceConfiguration(
            'test_service',
            '/++etc++Services/Packages/default/test_service2')
        default['configure'].setObject('', configuration)
        traverse(default, 'configure/2').status = Registered

        testOb = getService(self.rootFolder, 'test_service')
        self.assertEqual(testOb, ts1)


    def testUnbindService(self):

        root_ts = TestService()
        gsm = getServiceManager(None)
        gsm.provideService('test_service', root_ts)

        self.testGetService() # set up localservice

        sm = traverse(self.rootFolder, '++etc++Services')
        traverse(sm, 'Packages/default/configure/1').status = Unregistered

        self.assertEqual(getService(self.rootFolder, 'test_service'), root_ts)

    def testContextServiceLookup(self):
        self.testGetService() # set up localservice
        sm=getServiceManager(self.rootFolder)
        self.assertEqual(getService(self.folder1_1, 'test_service'),
                         sm.Packages['default']['test_service1'])

    def testContextServiceLookupWithMultipleServiceManagers(self):
        self.testGetService() # set up root localservice
        sm=getServiceManager(self.rootFolder)

        self.folder1.setServiceManager(ServiceManager())
        sm2=getServiceManager(self.folder1)

        self.assertEqual(getService(self.folder1, 'test_service'),
                         sm.Packages['default']['test_service1'])

    def testComponentArchitectureServiceLookup(self):
        self.rootFolder.setServiceManager(ServiceManager())
        self.folder1.setServiceManager(ServiceManager())

        ts = TestService()

        globsm=getServiceManager(None)
        globsm.provideService('test_service', ts)

        service = getService(self.folder1, 'test_service')
        self.assertEqual(service, ts)

    def test_resolve(self):
        from Zope.Proxy.ContextWrapper import ContextWrapper as cw
        from Zope.App.OFS.Services.ServiceManager.Module import Manager
        import Zope.App.OFS.Services.ServiceManager.tests.Sample1
        import Zope.App.OFS.Services.ServiceManager.tests.Sample2

        self.rootFolder.setServiceManager(ServiceManager())
        sm=getServiceManager(self.rootFolder)
        Packages = cw(sm.Packages, sm, name='Packages')
        default = cw(Packages['default'], Packages, name='Packages')
        default.setObject('m1', Manager())
        manager = cw(default['m1'], default, name='m1')
        manager.new('Zope.App.OFS.Services.ServiceManager.tests.Sample1',
                    'x = "root m1"\n')
        default.setObject('m2', Manager())
        manager = cw(default['m2'], default, name='m1')
        manager.new('XXX.ZZZ', 'x = "root m2"\nZZZ = 42\n')

        self.folder1.setServiceManager(ServiceManager())
        sm2=getServiceManager(self.folder1)
        Packages = cw(sm2.Packages, sm2, name='Packages')
        default = cw(Packages['default'], Packages, name='Packages')
        default.setObject('m1', Manager())
        manager = cw(default['m1'], default, name='m1')
        manager.new('Zope.App.OFS.Services.ServiceManager.tests.Sample1',
                    'x = "folder1 m1 1"')

        self.assertEqual(
          sm2.resolve("Zope.App.OFS.Services.ServiceManager.tests.Sample1.x"),
          "folder1 m1 1")
        self.assertEqual(
          sm.resolve("Zope.App.OFS.Services.ServiceManager.tests.Sample1.x"),
          "root m1")

        self.assertEqual(
          sm2.resolve("Zope.App.OFS.Services.ServiceManager.tests.Sample2.y"),
          "sample 2")
        self.assertEqual(
          sm.resolve("Zope.App.OFS.Services.ServiceManager.tests.Sample2.y"),
          "sample 2")

        self.assertEqual(sm.resolve("XXX.ZZZ.ZZZ"), 42)
        self.assertEqual(sm.resolve("XXX.ZZZ."), 42)
        self.assertEqual(sm.resolve("XXX.ZZZ.x"), "root m2")

        self.assertEqual(sm2.resolve("XXX.ZZZ.ZZZ"), 42)
        self.assertEqual(sm2.resolve("XXX.ZZZ."), 42)
        self.assertEqual(sm2.resolve("XXX.ZZZ.x"), "root m2")


def test_suite():
    loader=TestLoader()
    return loader.loadTestsFromTestCase(ServiceManagerTests)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
