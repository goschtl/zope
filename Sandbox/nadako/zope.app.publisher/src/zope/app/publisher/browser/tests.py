##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""'browser' namespace directive tests

$Id$
"""

import sys
import os
import unittest
from cStringIO import StringIO

from zope import component
from zope.interface import Interface, implements, directlyProvides, providedBy

import zope.security.management
from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces import IDefaultViewName
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserSkinType, IDefaultSkin
from zope.security.proxy import removeSecurityProxy, ProxyFactory
from zope.security.permission import Permission
from zope.security.interfaces import IPermission
from zope.testing.doctestunit import DocTestSuite
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.interfaces import ITraversable

import zope.publisher.defaultview
import zope.app.publisher.browser
from zope.component.testfiles.views import IC, V1, VZMI, R1, IV
from zope.app.publisher.browser.fileresource import FileResource
from zope.app.publisher.browser.i18nfileresource import I18nFileResource
from zope.browsermenu.menu import getFirstMenuItem
from zope.browsermenu.interfaces import IMenuItemType, IBrowserMenu
from zope.app.testing import placelesssetup, ztapi

tests_path = os.path.join(
    os.path.dirname(zope.app.publisher.browser.__file__),
    'tests')

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'>
   %s
   </configure>"""


request = TestRequest()

class V2(V1, object):

    def action(self):
        return self.action2()

    def action2(self):
        return "done"

class VT(V1, object):
    def publishTraverse(self, request, name):
        try:
            return int(name)
        except:
            return super(VT, self).publishTraverse(request, name)

class Ob(object):
    implements(IC)

ob = Ob()

class NCV(object):
    "non callable view"

    def __init__(self, context, request):
        pass

class CV(NCV):
    "callable view"
    def __call__(self):
        pass


class C_w_implements(NCV):
    implements(Interface)

    def index(self):
        return self

class ITestMenu(Interface):
    """Test menu."""

directlyProvides(ITestMenu, IMenuItemType)


class ITestLayer(IBrowserRequest):
    """Test Layer."""

class ITestSkin(ITestLayer):
    """Test Skin."""


class MyResource(object):

    def __init__(self, request):
        self.request = request


class Test(placelesssetup.PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.app.publisher.browser)()
        ztapi.provideAdapter(None, ITraversable, DefaultTraversable)

    def testDefaultView(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, request), IDefaultViewName),
            None)

        xmlconfig(StringIO(template % (
            '''
            <browser:defaultView
                name="test"
                for="zope.component.testfiles.views.IC" />
            '''
            )))

        self.assertEqual(
            zope.publisher.defaultview.getDefaultViewName(ob, request),
            'test')

    def testDefaultViewWithLayer(self):
        class FakeRequest(TestRequest):
            implements(ITestLayer)
        request2 = FakeRequest()

        self.assertEqual(
            component.queryMultiAdapter((ob, request2), IDefaultViewName),
            None)

        xmlconfig(StringIO(template % (
            '''
            <browser:defaultView
                name="test"
                for="zope.component.testfiles.views.IC" />

            <browser:defaultView
                name="test2"
                for="zope.component.testfiles.views.IC"
                layer="
                  zope.app.publisher.browser.tests.ITestLayer"
                />
            '''
            )))

        self.assertEqual(
            zope.publisher.defaultview.getDefaultViewName(ob, request2),
            'test2')
        self.assertEqual(
            zope.publisher.defaultview.getDefaultViewName(ob, request),
            'test')

    def testDefaultViewForClass(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, request), IDefaultViewName),
            None)

        xmlconfig(StringIO(template % (
            '''
            <browser:defaultView
                for="zope.app.publisher.browser.tests.Ob"
                name="test"
                />
            '''
            )))

        self.assertEqual(
            zope.publisher.defaultview.getDefaultViewName(ob, request),
            'test')

    def testDefaultSkin(self):
        request = TestRequest()
        self.assertEqual(
            component.queryMultiAdapter((ob, request), name='test'),
            None)

        XMLConfig('meta.zcml', zope.component)()
        xmlconfig(StringIO(template % (
            '''
            <interface
                interface="
                  zope.app.publisher.browser.tests.ITestSkin"
                type="zope.publisher.interfaces.browser.IBrowserSkinType"
                name="Test Skin"
                />
            <browser:defaultSkin name="Test Skin" />
            <browser:page
                name="test"
                class="zope.component.testfiles.views.VZMI"
                layer="
                  zope.app.publisher.browser.tests.ITestLayer"
                for="zope.component.testfiles.views.IC"
                permission="zope.Public"
                attribute="index"
                />
            <browser:page name="test"
                class="zope.component.testfiles.views.V1"
                for="zope.component.testfiles.views.IC"
                permission="zope.Public"
                attribute="index"
                />
            '''
            )))

        # Simulate Zope Publication behavior in beforeTraversal()
        adapters = component.getSiteManager().adapters
        skin = adapters.lookup((providedBy(request),), IDefaultSkin, '')
        directlyProvides(request, skin)

        v = component.queryMultiAdapter((ob, request), name='test')
        self.assert_(issubclass(v.__class__, VZMI))

def test_suite():
    return unittest.makeSuite(Test)
