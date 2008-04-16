##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id$
"""

import unittest
import zope.component
from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import PlacelessSetup

from zope.annotation.attribute import AttributeAnnotations
from zope.publisher.interfaces import NotFound
from zope.publisher.http import HTTPCharsets
from zope.publisher.browser import TestRequest

from z3c.resource import adapter
from z3c.resource import testing
from z3c.resource.browser.views import Resources


class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        zope.component.provideAdapter(HTTPCharsets)
        zope.component.provideAdapter(AttributeAnnotations)
        zope.component.provideAdapter(adapter.getResource)

    def test_publishTraverse(self):
        
        request = TestRequest()

        class ResourceItem(testing.TestResourceItem):
            def __init__(self, request): pass
            def __call__(self): return 42

        ztapi.browserResource('test', ResourceItem)
        content = testing.Content()
        view = Resources(content, request)
        result = view.publishTraverse(request, 'test')
        self.assertEqual(result(), 42)

    def test_getitem(self):
        request = TestRequest()

        class ResourceItem(testing.TestResourceItem):
            def __init__(self, request): pass
            def __call__(self): return 42

        ztapi.browserResource('test', ResourceItem)
        content = testing.Content()
        view = Resources(content, request)
        result = view['test']
        self.assertEqual(result(), 42)

    def testNotFound(self):
        request = TestRequest()
        content = testing.Content()
        view = Resources(content, request)
        self.assertRaises(NotFound,
                          view.publishTraverse,
                          request, 'test'
                          )


def test_suite():
    return unittest.makeSuite(Test)


if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
