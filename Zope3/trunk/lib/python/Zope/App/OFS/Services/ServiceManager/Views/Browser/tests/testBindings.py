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

$Id: testBindings.py,v 1.2 2002/06/10 23:28:13 jim Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Interface import Interface

from Zope.App.OFS.Services.ServiceManager.Views.Browser.Bindings \
    import Bindings
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup import \
    PlacefulSetup
from Zope.ComponentArchitecture import getService, getServiceManager

class ITestService1(Interface): pass
class ITestService2(Interface): pass

class TestService1:

    __implements__ = ITestService1

class TestService2:

    __implements__ = ITestService2


class ServiceManagerTests(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.createServiceManager()
        self.sm=getServiceManager(self.rootFolder)
        getServiceManager(None).defineService('service1', ITestService1)
        getServiceManager(None).defineService('service2', ITestService2)

        sA = TestService1()
        sB = TestService1()
        sC = TestService2()

        self.sm.setObject('TestServiceA', sA)
        self.sm.setObject('TestServiceB', sB)
        self.sm.setObject('TestServiceC', sC)

        self.sm.bindService('service1', 'TestServiceA')

    def testGetServicesTable(self):
        view = Bindings(self.sm, None)
        self.assertEqual(len(view.getServicesTable()), 8) #that is, 2+6

    def testServiceTableBound(self):
        view = Bindings(self.sm, None)
        services = view.getServicesTable()
        serviceMap = None
        for sMap in services:
            if sMap['name'] == 'service1':
                serviceMap = sMap
                break
            
        self.assertEqual(serviceMap['bound'], 'TestServiceA')

## XXX Was commented:
## """This test is not working (bug in getServicesTable(), returning
## 'Acquired' instead of 'None'"""
##
## Then further commented:
## However, we're now acquiring from the globally defined services,
## so it is appropriate to return 'Acquired'.
##
## To which I now add:
## I actually think that it should be 'None' after all.  Where is
## service2 provided globally?
##        
    def testServiceTableNone(self):
        view = Bindings(self.sm, None)
        services = view.getServicesTable()
        serviceMap = None
        for sMap in services:
            if sMap['name'] == 'service2':
                serviceMap = sMap
                break
        self.assertEqual(serviceMap['bound'], 'None')

def test_suite():
    return TestSuite([makeSuite(ServiceManagerTests)])

if __name__=='__main__':
    main(defaultTest='test_suite')
