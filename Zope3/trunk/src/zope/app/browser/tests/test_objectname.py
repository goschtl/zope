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
$Id: test_objectname.py,v 1.3 2002/12/31 02:51:56 jim Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.interface import Interface

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component import getService, getView, getAdapter

from zope.i18n.interfaces import IUserPreferredCharsets

from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.publisher.tests.httprequest import TestRequest
from zope.publisher.http import IHTTPRequest
from zope.publisher.http import HTTPCharsets

from zope.proxy.context import ContextWrapper

from zope.app.browser.objectname \
    import ObjectNameView, SiteObjectNameView

class IRoot(Interface): pass

class Root:
    __implements__ = IRoot

class TrivialContent(object):
    """Trivial content object, used because instances of object are rocks."""

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideView = getService(None, "Views").provideView
        provideView(None, 'object_name', IBrowserPresentation,
                    [ObjectNameView])
        provideView(IRoot, 'object_name', IBrowserPresentation,
                    [SiteObjectNameView])

        provideAdapter = getService(None, "Adapters").provideAdapter
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)

    def testViewBadObject(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)
        view = getView(None, 'object_name', request)
        self.assertRaises(TypeError, view.__str__)

    def testViewNoContext(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)
        view = getView(Root(), 'object_name', request)
        self.assertRaises(TypeError, str(view))

    def testViewBasicContext(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        content = ContextWrapper(TrivialContent(), Root(), name='a')
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        view = getView(content, 'object_name', request)
        self.assertEqual(str(view), 'c')

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
