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
$Id: test_servicemanager.py,v 1.7 2003/03/24 11:09:40 jim Exp $
"""
from unittest import TestCase, TestLoader, TextTestRunner

from zope.interface import Interface
from zope.app.content.folder import RootFolder
from zope.app.content.folder import Folder
from zope.proxy.context import getWrapperContext, getWrapperContainer
from zope.app.services.service import ServiceManager
from zope.app.services.service import ServiceConfiguration
from zope.component import getService, getServiceManager
from zope.exceptions import ZopeError
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse
from zope.app.interfaces.services.configuration import Active, Unregistered
from zope.app.interfaces.services.configuration import Registered
from zope.component.service import serviceManager

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
        sm = traverse(self.rootFolder, '++etc++site')
        default = traverse(sm, 'default')

        ts = TestService()
        default.setObject('test_service1', ts)
        configuration = ServiceConfiguration(
            'test_service',
            '/++etc++site/default/test_service1')

        default.getConfigurationManager().setObject('', configuration)
        traverse(default.getConfigurationManager(), '1').status = Active

        testOb = getService(self.rootFolder, 'test_service')
        c = getWrapperContainer
        self.assertEqual(c(c(c(testOb))), self.rootFolder)
        self.assertEqual(testOb, ts)

    def test_queryLocalService(self):
        self.createServiceManager()
        sm = traverse(self.rootFolder, '++etc++site')

        # Test no service case
        self.assertEqual(sm.queryLocalService('test_service'), None)
        self.assertEqual(sm.queryLocalService('test_service', 42), 42)

        # Test Services special case
        self.assertEqual(sm.queryLocalService('Services', 42), sm)

        # Test found local
        default = traverse(sm, 'default')
        ts = TestService()
        default.setObject('test_service1', ts)
        configuration = ServiceConfiguration(
            'test_service',
            '/++etc++site/default/test_service1')
        default.getConfigurationManager().setObject('', configuration)
        traverse(default.getConfigurationManager(), '1').status = Active

        testOb = sm.queryLocalService('test_service')
        c = getWrapperContainer
        self.assertEqual(c(c(c(testOb))), self.rootFolder)
        self.assertEqual(testOb, ts)


    def test_get(self):
        self.createServiceManager()
        sm = traverse(self.rootFolder, '++etc++site')
        default = sm.get('default')
        self.assertEqual(default, sm.Packages['default'])
        self.assertEqual(sm.get('spam'), None)

    def testAddService(self):
        self.createServiceManager()
        sm = traverse(self.rootFolder, '++etc++site')
        default = traverse(sm, 'default')

        ts1 = TestService()
        default.setObject('test_service1', ts1)
        configuration = ServiceConfiguration(
            'test_service',
            '/++etc++site/default/test_service1')
        default.getConfigurationManager().setObject('', configuration)
        traverse(default.getConfigurationManager(), '1').status = Active

        ts2 = TestService()
        default.setObject('test_service2', ts2)
        configuration = ServiceConfiguration(
            'test_service',
            '/++etc++site/default/test_service2')
        default.getConfigurationManager().setObject('', configuration)
        traverse(default.getConfigurationManager(), '2').status = Registered

        testOb = getService(self.rootFolder, 'test_service')
        self.assertEqual(testOb, ts1)


    def testUnbindService(self):

        root_ts = TestService()
        gsm = getServiceManager(None)
        gsm.provideService('test_service', root_ts)

        self.testGetService() # set up localservice

        sm = traverse(self.rootFolder, '++etc++site')
        cm = traverse(sm, 'default').getConfigurationManager()
        traverse(cm, '1').status = Unregistered

        self.assertEqual(getService(self.rootFolder, 'test_service'), root_ts)

    def testContextServiceLookup(self):
        self.testGetService() # set up localservice
        sm=getServiceManager(self.rootFolder)
        self.assertEqual(getService(self.folder1_1, 'test_service'),
                         sm['default']['test_service1'])

    def testContextServiceLookupWithMultipleServiceManagers(self):
        self.testGetService() # set up root localservice
        sm=getServiceManager(self.rootFolder)

        self.folder1.setServiceManager(ServiceManager())
        sm2=getServiceManager(self.folder1)

        self.assertEqual(getService(self.folder1, 'test_service'),
                         sm['default']['test_service1'])

    def testComponentArchitectureServiceLookup(self):
        self.rootFolder.setServiceManager(ServiceManager())
        self.folder1.setServiceManager(ServiceManager())

        ts = TestService()

        globsm=getServiceManager(None)
        globsm.provideService('test_service', ts)

        service = getService(self.folder1, 'test_service')
        self.assertEqual(service, ts)

    def test_resolve(self):
        from zope.proxy.context import ContextWrapper as cw
        from zope.app.services.module import Manager
        import zope.app.services.tests.sample1
        import zope.app.services.tests.sample2

        self.rootFolder.setServiceManager(ServiceManager())
        sm=getServiceManager(self.rootFolder)
        default = cw(sm['default'], self.rootFolder, name='default')
        default.setObject('m1', Manager())
        manager = cw(default['m1'], default, name='m1')
        manager.new('zope.app.services.tests.sample1',
                    'x = "root m1"\n')
        default.setObject('m2', Manager())
        manager = cw(default['m2'], default, name='m2')
        manager.new('XXX.ZZZ', 'x = "root m2"\nZZZ = 42\n')

        self.folder1.setServiceManager(ServiceManager())
        sm2=getServiceManager(self.folder1)
        default = cw(sm2['default'], self.folder1, name='default')
        default.setObject('m1', Manager())
        manager = cw(default['m1'], default, name='m1')
        manager.new('zope.app.services.tests.sample1',
                    'x = "folder1 m1 1"')

        self.assertEqual(
          sm2.resolve("zope.app.services.tests.sample1.x"),
          "folder1 m1 1")
        self.assertEqual(
          sm.resolve("zope.app.services.tests.sample1.x"),
          "root m1")

        self.assertEqual(
          sm2.resolve("zope.app.services.tests.sample2.y"),
          "sample 2")
        self.assertEqual(
          sm.resolve("zope.app.services.tests.sample2.y"),
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
