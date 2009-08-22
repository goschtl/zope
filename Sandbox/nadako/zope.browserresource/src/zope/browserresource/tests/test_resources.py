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
"""Test Browser Resources

$Id: test_resources.py 67630 2006-04-27 00:54:03Z jim $
"""
from unittest import TestCase, main, makeSuite

from zope.i18n.interfaces import IUserPreferredCharsets
from zope.publisher.http import IHTTPRequest
from zope.publisher.http import HTTPCharsets
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserView, IDefaultBrowserLayer

from zope.component import provideAdapter
from zope.interface import Interface
from zope.testing.cleanup import CleanUp

class Test(CleanUp, TestCase):

    def setUp(self):
        super(Test, self).setUp()
        provideAdapter(HTTPCharsets, (IHTTPRequest,), IUserPreferredCharsets)

    def test_publishTraverse(self):
        from zope.browserresource.resources import Resources
        request = TestRequest()

        class Resource(object):
            def __init__(self, request): pass
            def __call__(self): return 42

        provideAdapter(Resource, (IDefaultBrowserLayer,), Interface, 'test')
        view = Resources(None, request)
        resource = view.publishTraverse(request, 'test')
        self.assertEqual(resource(), 42)

    def test_getitem(self):
        from zope.browserresource.resources import Resources
        request = TestRequest()

        class Resource(object):
            def __init__(self, request): pass
            def __call__(self): return 42

        provideAdapter(Resource, (IDefaultBrowserLayer,), Interface, 'test')
        view = Resources(None, request)
        resource = view['test']
        self.assertEqual(resource(), 42)

    def testNotFound(self):
        from zope.browserresource.resources import Resources
        from zope.publisher.interfaces import NotFound
        request = TestRequest()
        view = Resources(None, request)
        self.assertRaises(NotFound,
                          view.publishTraverse,
                          request, 'test'
                          )



def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
