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
$Id: test_absoluteurl.py,v 1.16 2003/09/21 17:31:10 jim Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.interface import Interface, implements

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component import getService, getView
from zope.app.services.servicenames import Adapters, Views

from zope.i18n.interfaces import IUserPreferredCharsets

from zope.publisher.tests.httprequest import TestRequest
from zope.publisher.http import IHTTPRequest
from zope.publisher.http import HTTPCharsets
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.container.contained import contained


class IRoot(Interface): pass

class Root:
    implements(IRoot)

class TrivialContent(object):
    """Trivial content object, used because instances of object are rocks."""

class TestAbsoluteURL(PlacelessSetup, TestCase):

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
        view = getView(42, 'absolute_url', request)
        self.assertRaises(TypeError, view.__str__)

    def testNoContext(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)
        view = getView(Root(), 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com')

    def testBasicContext(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        content = contained(TrivialContent(), Root(), name='a')
        content = contained(TrivialContent(), content, name='b')
        content = contained(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/a/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
                         ({'name':  '', 'url': 'http://foobar.com'},
                          {'name': 'a', 'url': 'http://foobar.com/a'},
                          {'name': 'b', 'url': 'http://foobar.com/a/b'},
                          {'name': 'c', 'url': 'http://foobar.com/a/b/c'},
                          ))

    def testVirtualHosting(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        vh_root = TrivialContent()
        content = contained(vh_root, Root(), name='a')
        request._vh_root = content
        content = contained(TrivialContent(), content, name='b')
        content = contained(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
         ({'name':  '', 'url': 'http://foobar.com'},
          {'name': 'b', 'url': 'http://foobar.com/b'},
          {'name': 'c', 'url': 'http://foobar.com/b/c'},
          ))

    def testVirtualHostingWithVHElements(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        vh_root = TrivialContent()
        content = contained(vh_root, Root(), name='a')
        request._vh_root = content
        content = contained(TrivialContent(), content, name='b')
        content = contained(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
         ({'name':  '', 'url': 'http://foobar.com'},
          {'name': 'b', 'url': 'http://foobar.com/b'},
          {'name': 'c', 'url': 'http://foobar.com/b/c'},
          ))

    def testVirtualHostingInFront(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        root = Root()
        request._vh_root = contained(root, root, name='')
        content = contained(root, None)
        content = contained(TrivialContent(), content, name='a')
        content = contained(TrivialContent(), content, name='b')
        content = contained(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/a/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
         ({'name':  '', 'url': 'http://foobar.com'},
          {'name': 'a', 'url': 'http://foobar.com/a'},
          {'name': 'b', 'url': 'http://foobar.com/a/b'},
          {'name': 'c', 'url': 'http://foobar.com/a/b/c'},
          ))


def test_suite():
    return makeSuite(TestAbsoluteURL)

if __name__=='__main__':
    main(defaultTest='test_suite')
