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

$Id: test_addservicecontainer.py,v 1.2 2002/12/25 14:12:38 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup \
     import PlacefulSetup
from zope.component.service import defineService
from zope.interface import Interface
from zope.app.services.service import ServiceManager
from zope.component import getServiceManager
from zope.app.browser.services.service \
     import AddServiceConfiguration
from zope.publisher.browser import TestRequest
from zope.app.browser.services.service import ComponentAdding
from zope.app.browser.services.package \
     import PackagesContents

from zope.component import getService

from zope.component.exceptions import ComponentLookupError

from zope.app.browser.absoluteurl \
     import AbsoluteURL, SiteAbsoluteURL
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.interfaces.content.folder import IRootFolder
from zope.component.adapter import provideAdapter
from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.container import IContainer
from zope.app.container.zopecontainer import ZopeContainerAdapter

from zope.app.interfaces.annotation import IAnnotatable
from zope.app.interfaces.annotation \
     import IAttributeAnnotatable
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.dependable import IDependable
from zope.app.dependable import Dependable

from zope.app.traversing import traverse

from zope.component.view import provideView
from zope.component.view import setDefaultViewName

from zope.app.interfaces.services.configuration import IConfigurationStatus
from zope.app.browser.services.configurationstatuswidget \
     import ConfigurationStatusWidget

from zope.schema.interfaces import IField, ITextLine, IText
from zope.app.browser.form.widget import TextWidget, TextAreaWidget

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

        setDefaultViewName(IField, IBrowserPresentation, 'edit')
        provideView(IConfigurationStatus, 'edit', IBrowserPresentation,
                    ConfigurationStatusWidget)
        provideView(ITextLine, 'edit', IBrowserPresentation, TextWidget)
        provideView(IText, 'edit', IBrowserPresentation, TextAreaWidget)

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
