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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: testAddServiceDirective.py,v 1.1 2002/07/11 18:21:33 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
     import PlacefulSetup
from Zope.ComponentArchitecture.GlobalServiceManager \
     import defineService
from Interface import Interface
from Zope.App.OFS.Services.ServiceManager.ServiceManager \
     import ServiceManager
from Zope.ComponentArchitecture import getServiceManager
from Zope.App.OFS.Services.ServiceManager.Views.Browser.AddServiceDirective \
     import AddServiceDirective
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.App.OFS.Services.ServiceManager.Views.Browser.Adding \
     import ComponentAdding
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.App.OFS.Services.ServiceManager.Views.Browser.PackagesContents \
     import PackagesContents

from Zope.App.Traversing.Traverser import Traverser
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.App.Traversing.DefaultTraversable import DefaultTraversable
from Zope.App.Traversing.ITraversable import ITraversable


from Zope.App.Traversing.IPhysicallyLocatable import IPhysicallyLocatable
from Zope.App.Traversing.IContainmentRoot import IContainmentRoot
from Zope.App.Traversing.PhysicalLocationAdapters \
     import WrapperPhysicallyLocatable, RootPhysicallyLocatable


from Zope.App.OFS.Container.ContainerTraversable import ContainerTraversable
from Zope.App.OFS.Container.IContainer import ISimpleReadContainer

from Zope.ComponentArchitecture import getService

from Zope.ComponentArchitecture.Exceptions import ComponentLookupError

from Zope.App.ZopePublication.TraversalViews.AbsoluteURL \
     import AbsoluteURL, SiteAbsoluteURL
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.App.OFS.Content.Folder.RootFolder import IRootFolder

class I1(Interface): pass
class C: __implements__ = I1

class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()

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

        defineService('s1', I1)
        self.folder1_1.setServiceManager(ServiceManager())

        viewService = getService(None, "Views")
        viewService.provideView(None, "absolute_url", IBrowserPresentation,
                                AbsoluteURL)
        viewService.provideView(IRootFolder, "absolute_url",
                                IBrowserPresentation,
                                SiteAbsoluteURL)
        

    def test_services(self):
        
        class I2(Interface): pass
        class I3(Interface): pass
        defineService('s2', I2)
        defineService('s3', I3)
        sm = getServiceManager(self.folder1_1_1)
        request = TestRequest()
        packages = ContextWrapper(sm.Packages, sm, name="Packages")
        view = AddServiceDirective(
            ComponentAdding(ContextWrapper(packages['default'], packages,
                                           name='default'),
                            request),
            request)
        services = list(view.services())
        services.sort()
        self.failUnless((('s1' in services) and
                         ('s2' in services) and
                         ('s3' in services)), services) 

    def test_components(self):

        sm = getServiceManager(self.folder1_1_1)
        request = TestRequest(service_type='s1')
        packages = ContextWrapper(sm.Packages, sm, name="Packages")
        PackagesContents(packages, request).addPackage('p1')
        PackagesContents(packages, request).addPackage('p2')

        packages['default'].setObject('cd1', C())
        packages['default'].setObject('cd2', C())
        packages['p1'].setObject('c11', C())
        packages['p2'].setObject('c21', C())
        packages['p2'].setObject('c22', C())

        view = AddServiceDirective(
            ComponentAdding(ContextWrapper(packages['default'], packages,
                                           name='default'),
                            request),
            request)
        
        components = list(view.components())
        components.sort()

        self.assertEqual(
            components,
            ['/folder1/folder1_1/++etc++Services/Packages/default/cd1',
             '/folder1/folder1_1/++etc++Services/Packages/default/cd2',
             '/folder1/folder1_1/++etc++Services/Packages/p1/c11',
             '/folder1/folder1_1/++etc++Services/Packages/p2/c21',
             '/folder1/folder1_1/++etc++Services/Packages/p2/c22'])

    def test_action_unregistered(self):
        sm = getServiceManager(self.folder1_1_1)
        packages = ContextWrapper(sm.Packages, sm, name="Packages")
        request = TestRequest()
        service = C()
        packages['default'].setObject('cd1', service)

        view = AddServiceDirective(
            ComponentAdding(ContextWrapper(packages['default'], packages,
                                           name='default'),
                            request),
            request)

        view.action('s1',
                    '/folder1/folder1_1/++etc++Services/Packages/default/cd1',
                    )
        self.assertRaises(ComponentLookupError, getService,
                          self.folder1_1_1, 's1')

    def test_action_active(self):
        sm = getServiceManager(self.folder1_1_1)
        packages = ContextWrapper(sm.Packages, sm, name="Packages")
        request = TestRequest()
        service = C()
        packages['default'].setObject('cd1', service)

        view = AddServiceDirective(
            ComponentAdding(ContextWrapper(packages['default'], packages,
                                           name='default'),
                            request),
            request)

        view.action('s1',
                    '/folder1/folder1_1/++etc++Services/Packages/default/cd1',
                    'active')
        self.assertEqual(getService(self.folder1_1_1, 's1'), service)

    def test_action_register(self):
        sm = getServiceManager(self.folder1_1_1)
        packages = ContextWrapper(sm.Packages, sm, name="Packages")
        request = TestRequest()
        service = C()
        packages['default'].setObject('cd1', service)

        view = AddServiceDirective(
            ComponentAdding(ContextWrapper(packages['default'], packages,
                                           name='default'),
                            request),
            request)

        view.action('s1',
                    '/folder1/folder1_1/++etc++Services/Packages/default/cd1',
                    'active')

        service2 = C()
        packages['default'].setObject('cd2', service2)
        view.action('s1',
                    '/folder1/folder1_1/++etc++Services/Packages/default/cd2',
                    'register')


        self.assertEqual(getService(self.folder1_1_1, 's1'), service)


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
