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

$Id: testBindings.py,v 1.4 2002/07/11 19:30:42 jim Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Interface import Interface

from Zope.App.OFS.Services.ServiceManager.Views.Browser.Bindings \
    import Bindings
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup import \
    PlacefulSetup
from Zope.ComponentArchitecture import getService, getServiceManager
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.App.Traversing import getPhysicalPathString


from Zope.App.Traversing.Traverser import Traverser
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.App.Traversing.DefaultTraversable import DefaultTraversable
from Zope.App.Traversing.ITraversable import ITraversable

from Zope.App.OFS.Container.ContainerTraversable import ContainerTraversable
from Zope.App.OFS.Container.IContainer import ISimpleReadContainer


from Zope.App.Traversing.IPhysicallyLocatable import IPhysicallyLocatable
from Zope.App.Traversing.IContainmentRoot import IContainmentRoot
from Zope.App.Traversing.PhysicalLocationAdapters \
     import WrapperPhysicallyLocatable, RootPhysicallyLocatable

from Zope.App.OFS.Services.ServiceManager.ServiceDirective \
     import ServiceDirective


from Zope.App.ZopePublication.TraversalViews.AbsoluteURL \
     import AbsoluteURL, SiteAbsoluteURL
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.App.OFS.Content.Folder.RootFolder import IRootFolder


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
        self.sm = sm = getServiceManager(self.rootFolder)
        getServiceManager(None).defineService('service1', ITestService1)
        getServiceManager(None).defineService('service2', ITestService2)

        adapterService = getService(None, "Adapters")

        adapterService.provideAdapter(
            None, ITraverser, Traverser)
        adapterService.provideAdapter(
            None, ITraversable, DefaultTraversable)
        adapterService.provideAdapter(
            ISimpleReadContainer, ITraversable, ContainerTraversable)


        adapterService.provideAdapter(
              None, IPhysicallyLocatable, WrapperPhysicallyLocatable)
        adapterService.provideAdapter(
              IContainmentRoot, IPhysicallyLocatable, RootPhysicallyLocatable)


        viewService = getService(None, "Views")
        viewService.provideView(None, "absolute_url", IBrowserPresentation,
                                AbsoluteURL)
        viewService.provideView(IRootFolder, "absolute_url",
                                IBrowserPresentation,
                                SiteAbsoluteURL)


        sA = TestService1()
        sB = TestService1()
        sC = TestService2()

        sm.Packages['default'].setObject('TestServiceA', sA)
        sm.Packages['default'].setObject('TestServiceB', sB)
        sm.Packages['default'].setObject('TestServiceC', sC)

        path = "%s/Packages/default/TestServiceA" % getPhysicalPathString(sm)
        directive = ServiceDirective("service1", path)
        sm.Packages['default'].setObject("DirA", directive)
        sm.bindService(directive)

    def testGetServicesTable(self):
        view = Bindings(self.sm, TestRequest())
        self.assertEqual(view.getServicesTable(), [
            {'active': 1,
             'inactive': None,
             'name': 'service1',
             'directives': [
                {
            'sm_url': 'http://127.0.0.1/++etc++Services/Packages',
            'sm_path': '',
            'component_path': '/++etc++Services/Packages/default/TestServiceA',
            'component_url':
              'http://127.0.0.1/++etc++Services/Packages/default/TestServiceA',
                 }
                ],
             }
            ])

def test_suite():
    return TestSuite([makeSuite(ServiceManagerTests)])

if __name__=='__main__':
    main(defaultTest='test_suite')
