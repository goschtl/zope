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
"""File-based browser resource tests.

$Id$
"""
import os
from unittest import TestCase, main, makeSuite

from zope.publisher.interfaces import NotFound
from zope.i18n.interfaces import IUserPreferredCharsets
from zope.security.proxy import removeSecurityProxy
from zope.security.checker import NamesChecker

from zope.testing import cleanup
from zope.component import provideAdapter

from zope.publisher.http import IHTTPRequest
from zope.publisher.http import HTTPCharsets
from zope.publisher.browser import TestRequest

from zope.browserresource.fileresource import FileResourceFactory
from zope.browserresource.fileresource import ImageResourceFactory
import zope.browserresource.tests as p

checker = NamesChecker(
    ('__call__', 'HEAD', 'request', 'publishTraverse', 'GET')
    )

test_directory = os.path.dirname(p.__file__)

class Test(cleanup.CleanUp, TestCase):

    def setUp(self):
        super(Test, self).setUp()
        provideAdapter(HTTPCharsets, (IHTTPRequest,), IUserPreferredCharsets)

    def testNoTraversal(self):

        path = os.path.join(test_directory, 'testfiles', 'test.txt')
        factory = FileResourceFactory(path, checker, 'test.txt')
        resource = factory(TestRequest())
        self.assertRaises(NotFound,
                          resource.publishTraverse,
                          resource.request,
                          '_testData')

    def testFileGET(self):

        path = os.path.join(test_directory, 'testfiles', 'test.txt')

        factory = FileResourceFactory(path, checker, 'test.txt')
        resource = factory(TestRequest())
        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = removeSecurityProxy(resource.request).response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

    def testFileHEAD(self):

        path = os.path.join(test_directory, 'testfiles', 'test.txt')
        factory = FileResourceFactory(path, checker, 'test.txt')
        resource = factory(TestRequest())

        self.assertEqual(resource.HEAD(), '')

        response = removeSecurityProxy(resource.request).response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

    def testBrowserDefault(self):
        path = os.path.join(test_directory, 'testfiles', 'test.txt')
        factory = FileResourceFactory(path, checker, 'test.txt')

        request = TestRequest(REQUEST_METHOD='GET')
        resource = factory(request)
        view, next = resource.browserDefault(request)
        self.assertEqual(view(), open(path, 'rb').read())
        self.assertEqual(next, ())

        request = TestRequest(REQUEST_METHOD='HEAD')
        resource = factory(request)
        view, next = resource.browserDefault(request)
        self.assertEqual(view(), '')
        self.assertEqual(next, ())

    def testImageGET(self):

        path = os.path.join(test_directory, 'testfiles', 'test.gif')

        factory = ImageResourceFactory(path, checker, 'test.gif')
        resource = factory(TestRequest())

        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = removeSecurityProxy(resource.request).response
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')

    def testImageHEAD(self):

        path = os.path.join(test_directory, 'testfiles', 'test.gif')
        factory = ImageResourceFactory(path, checker, 'test.gif')
        resource = factory(TestRequest())

        self.assertEqual(resource.HEAD(), '')

        response = removeSecurityProxy(resource.request).response
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')



def test_suite():
    return makeSuite(Test)
