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

$Id: testAddServiceContainer.py,v 1.2 2002/11/30 18:39:17 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
     import PlacefulSetup
from Zope.ComponentArchitecture.GlobalServiceManager import defineService
from Interface import Interface
from Zope.App.OFS.Services.ServiceManager.ServiceManager import ServiceManager
from Zope.ComponentArchitecture import getServiceManager
from Zope.App.OFS.Services.ServiceManager.Browser.AddServiceConfiguration \
     import AddServiceConfiguration
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.App.OFS.Services.ServiceManager.Browser.Adding import ComponentAdding
from Zope.App.OFS.Services.ServiceManager.Browser.PackagesContents \
     import PackagesContents

from Zope.ComponentArchitecture import getService

from Zope.ComponentArchitecture.Exceptions import ComponentLookupError

from Zope.App.ZopePublication.TraversalViews.AbsoluteURL \
     import AbsoluteURL, SiteAbsoluteURL
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.App.OFS.Content.Folder.RootFolder import IRootFolder
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter
from Zope.App.OFS.Container.IZopeContainer import IZopeContainer
from Zope.App.OFS.Container.IContainer import IContainer
from Zope.App.OFS.Container.ZopeContainerAdapter import ZopeContainerAdapter

from Zope.App.OFS.Annotation.IAnnotatable import IAnnotatable
from Zope.App.OFS.Annotation.IAttributeAnnotatable \
     import IAttributeAnnotatable
from Zope.App.OFS.Annotation.AttributeAnnotations import AttributeAnnotations
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.DependencyFramework.IDependable import IDependable
from Zope.App.DependencyFramework.Dependable import Dependable

from Zope.App.Traversing import traverse

from Zope.ComponentArchitecture.GlobalViewService import provideView
from Zope.ComponentArchitecture.GlobalViewService import setDefaultViewName

from Zope.App.OFS.Services.ConfigurationInterfaces import IConfigurationStatus
from Zope.App.OFS.Services.Browser.ConfigurationStatusWidget \
     import ConfigurationStatusWidget

from Zope.Schema.IField import IField, ITextLine, IText
from Zope.App.Forms.Views.Browser.Widget import TextWidget, TextAreaWidget

class I1(Interface): pass
class C: __implements__ = IAttributeAnnotatable, I1

class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        provideAdapter(IContainer, IZopeContainer, ZopeContainerAdapter)
        provideAdapter(IAttributeAnnotatable,
                       IAnnotations, AttributeAnnotations)
        provideAdapter(IAnnotatable, IDependable, Dependable)
        self.buildFolders()

        defineService('s1', I1)
        self.folder1_1.setServiceManager(ServiceManager())

        self.__Packages = traverse(
            self.rootFolder, "folder1/folder1_1/++etc++Services/Packages")
        self.__default = traverse(self.__Packages, 'default')

        setDefaultViewName(IField, IBrowserPresentation, "widget")
        provideView(IConfigurationStatus, "widget", IBrowserPresentation,
                    ConfigurationStatusWidget)
        provideView(ITextLine, "widget", IBrowserPresentation, TextWidget)
        provideView(IText, "widget", IBrowserPresentation, TextAreaWidget)

    def test_services(self):
        
        class I2(Interface): pass
        class I3(Interface): pass
        defineService('s2', I2)
        defineService('s3', I3)
        
        request = TestRequest()
        view = AddServiceConfiguration(
            ComponentAdding(self.__default, request), request)

        # We need the ContentAdding to have a contentName. It normally
        # gets set during traversal, but we aren't traversing here.
        view.context.contentName = 'sd1'

        services = list(view.services())
        services.sort()
        self.failUnless((('s1' in services) and
                         ('s2' in services) and
                         ('s3' in services)), services) 

    def test_components(self):

        request = TestRequest(service_type='s1')
        packages = self.__Packages
        PackagesContents(packages, request).addPackage('p1')
        PackagesContents(packages, request).addPackage('p2')

        packages['default'].setObject('cd1', C())
        packages['default'].setObject('cd2', C())
        packages['p1'].setObject('c11', C())
        packages['p2'].setObject('c21', C())
        packages['p2'].setObject('c22', C())

        view = AddServiceConfiguration(
            ComponentAdding(self.__default, request), request)

        # We need the ContentAdding to have a contentName. It normally
        # gets set during traversal, but we aren't traversing here.
        view.context.contentName = 'sd1'
        
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
        request = TestRequest()
        self.__default.setObject('cd1', C())

        view = AddServiceConfiguration(
            ComponentAdding(self.__default, request), request)

        # We need the ContentAdding to have a contentName. It normally
        # gets set during traversal, but we aren't traversing here.
        view.context.contentName = 'sd1'

        view.action('s1',
                    '/folder1/folder1_1/++etc++Services/Packages/default/cd1',
                    )
        self.assertRaises(ComponentLookupError,
                          getService, self.folder1_1_1, 's1')

    def test_action_active(self):
        service = C()
        self.__default.setObject('cd1', service)

        request = TestRequest()
        view = AddServiceConfiguration(
            ComponentAdding(self.__default, request), request)

        # We need the ContentAdding to have a contentName. It normally
        # gets set during traversal, but we aren't traversing here.
        view.context.contentName = 'sd1'

        request.form["field.status"] = u"Active"

        view.action('s1',
                    '/folder1/folder1_1/++etc++Services/Packages/default/cd1')
        self.assertEqual(getService(self.folder1_1_1, 's1'), service)

    def test_action_register(self):
        service = C()
        self.__default.setObject('cd1', service)

        request = TestRequest()
        view = AddServiceConfiguration(
            ComponentAdding(self.__default, request), request)

        # We need the ContentAdding to have a contentName. It normally
        # gets set during traversal, but we aren't traversing here.
        view.context.contentName = 'sd1'

        request.form["field.status"] = u"Active"

        view.action('s1',
                    '/folder1/folder1_1/++etc++Services/Packages/default/cd1')

        view.context.contentName = 'sd2'

        self.__default.setObject('cd2', C())

        request.form["field.status"] = u"Registered"

        view.action('s1',
                    '/folder1/folder1_1/++etc++Services/Packages/default/cd2')


        self.assertEqual(getService(self.folder1_1_1, 's1'), service)


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
