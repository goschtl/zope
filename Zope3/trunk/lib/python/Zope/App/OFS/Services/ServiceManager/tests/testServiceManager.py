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
$Id: testServiceManager.py,v 1.3 2002/07/11 18:21:33 jim Exp $
"""
from unittest import TestCase, TestLoader, TextTestRunner

from Interface import Interface
from Zope.App.OFS.Content.Folder.RootFolder import RootFolder
from Zope.App.OFS.Content.Folder.Folder import Folder
from Zope.Proxy.ContextWrapper import getWrapperContext, getWrapperContainer
from Zope.App.OFS.Services.ServiceManager.ServiceManager import ServiceManager
from Zope.App.OFS.Services.ServiceManager.ServiceDirective \
     import ServiceDirective
from Zope.ComponentArchitecture import getService, getServiceManager
from Zope.Exceptions import ZopeError
from PlacefulSetup import PlacefulSetup

from Zope.App.Traversing.IPhysicallyLocatable import IPhysicallyLocatable
from Zope.App.Traversing.IContainmentRoot import IContainmentRoot
from Zope.App.Traversing.PhysicalLocationAdapters \
     import WrapperPhysicallyLocatable, RootPhysicallyLocatable

class ITestService(Interface): pass

class TestService:

    __implements__ = ITestService

class ServiceManagerTests(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        from Zope.ComponentArchitecture.GlobalAdapterService \
             import provideAdapter
        from Zope.App.OFS.Services.ServiceManager.IServiceManager \
             import IServiceManager
        from Zope.App.Traversing.ITraversable import ITraversable
        from Zope.App.OFS.Container.IContainer import ISimpleReadContainer
        from Zope.App.OFS.Container.ContainerTraversable \
             import ContainerTraversable

        provideAdapter(ISimpleReadContainer, ITraversable,
                       ContainerTraversable)
        provideAdapter(
              None, IPhysicallyLocatable, WrapperPhysicallyLocatable)
        provideAdapter(
              IContainmentRoot, IPhysicallyLocatable, RootPhysicallyLocatable)

        from Zope.ComponentArchitecture.GlobalServiceManager \
             import serviceManager

        serviceManager.defineService('test_service', ITestService)

    def _Test__new(self):
        return ServiceManager()

    def testGetService(self):
        sm = ServiceManager()
        self.rootFolder.setServiceManager(sm)
        sm = getServiceManager(self.rootFolder)
        ts = TestService()
        sm.Packages['default'].setObject('test_service1', ts)
        directive = ServiceDirective(
            'test_service',
            '/++etc++Services/Packages/default/test_service1')
        sm.Packages['default'].setObject('test_service1_dir', directive)
        sm.bindService(directive)

        testOb = getService(self.rootFolder, 'test_service')
        c = getWrapperContainer
        self.assertEqual(c(c(c(c(testOb)))), self.rootFolder)
        self.assertEqual(testOb, ts)

    def testAddService(self):
        sm = ServiceManager()
        self.rootFolder.setServiceManager(sm)
        sm = getServiceManager(self.rootFolder)
        ts = TestService()
        sm.Packages['default'].setObject('test_service1', ts)
        directive = ServiceDirective(
            'test_service',
            '/++etc++Services/Packages/default/test_service1')
        sm.Packages['default'].setObject('test_service1_dir', directive)
        sm.bindService(directive)

        ts2 = TestService()
        sm.Packages['default'].setObject('test_service2', ts)
        directive = ServiceDirective(
            'test_service',
            '/++etc++Services/Packages/default/test_service2')
        sm.Packages['default'].setObject('test_service2_dir', directive)
        sm.bindService(directive)

        testOb = getService(self.rootFolder, 'test_service')
        self.assertEqual(testOb, ts)


    def testUnbindService(self):

        root_ts = TestService()
        gsm = getServiceManager(None)
        gsm.provideService('test_service', root_ts)

        self.testGetService() # set up localservice

        sm = getServiceManager(self.rootFolder)

        directive = sm.Packages['default']['test_service1_dir']
        sm.unbindService(directive)
        self.assertEqual(getService(self.rootFolder, 'test_service'), root_ts)

    # XXX This should be a test on the adapter responsible for deleting.
    def __testDeleteService(self):
        """sure deleting a service generates a service generates a
        removed event."""
        self.rootFolder.setServiceManager(ServiceManager())
        sm=getServiceManager(self.rootFolder)
        ts = TestService()
        
        sm.setObject('test_service1', ts)
        sm.bindService('test_service', 'test_service1')
        self.assertEqual(getService(self.rootFolder, 'test_service'), ts)
        self.assertRaises(ZopeError, sm.__delitem__, 'test_service1')
    
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


        
def test_suite():
    loader=TestLoader()
    return loader.loadTestsFromTestCase(ServiceManagerTests)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
