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
"""Test the AbsoluteURL view

Revision information:
$Id: test_absoluteurl.py,v 1.5 2003/02/11 15:59:39 sidnei Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.interface import Interface

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component import getService, getView
from zope.component.servicenames import Adapters, Views

from zope.i18n.interfaces import IUserPreferredCharsets

from zope.publisher.tests.httprequest import TestRequest
from zope.publisher.http import IHTTPRequest
from zope.publisher.http import HTTPCharsets
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.proxy.context import ContextWrapper


class IRoot(Interface): pass

class Root:
    __implements__ = IRoot

class TrivialContent(object):
    """Trivial content object, used because instances of object are rocks."""

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        from zope.app.browser.absoluteurl \
             import AbsoluteURL, SiteAbsoluteURL
        provideView=getService(None,Views).provideView
        provideView(None, 'absolute_url', IBrowserPresentation,
                    [AbsoluteURL])
        provideView(IRoot, 'absolute_url', IBrowserPresentation,
                    [SiteAbsoluteURL])
        provideAdapter = getService(None, Adapters).provideAdapter
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)

    def testBadObject(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)
        view = getView(None, 'absolute_url', request)
        self.assertRaises(TypeError, view.__str__)

    def testNoContext(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)
        view = getView(Root(), 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com')

    def testBasicContext(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        content = ContextWrapper(TrivialContent(), Root(), name='a')
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/a/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
                         ({'name':  '', 'url': 'http://foobar.com'},
                          {'name': 'a', 'url': 'http://foobar.com/a'},
                          {'name': 'b', 'url': 'http://foobar.com/a/b'},
                          {'name': 'c', 'url': 'http://foobar.com/a/b/c'},
                          ))

    def testContextWSideEffectsInMiddle(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        content = ContextWrapper(TrivialContent(), Root(), name='a')
        content = ContextWrapper(TrivialContent(), content,
                                 name='.',
                                 side_effect_name="++skin++ZopeTop")
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/a/++skin++ZopeTop/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
         ({'name':  '', 'url': 'http://foobar.com'},
          {'name': 'a', 'url': 'http://foobar.com/a/++skin++ZopeTop'},
          {'name': 'b', 'url': 'http://foobar.com/a/++skin++ZopeTop/b'},
          {'name': 'c', 'url': 'http://foobar.com/a/++skin++ZopeTop/b/c'},
          ))

    def testContextWSideEffectsInFront(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        root = Root()
        content = ContextWrapper(root, root,
                                 name='.',
                                 side_effect_name="++skin++ZopeTop")
        content = ContextWrapper(TrivialContent(), content, name='a')
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/++skin++ZopeTop/a/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
         ({'name':  '', 'url': 'http://foobar.com/++skin++ZopeTop'},
          {'name': 'a', 'url': 'http://foobar.com/++skin++ZopeTop/a'},
          {'name': 'b', 'url': 'http://foobar.com/++skin++ZopeTop/a/b'},
          {'name': 'c', 'url': 'http://foobar.com/++skin++ZopeTop/a/b/c'},
          ))


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
