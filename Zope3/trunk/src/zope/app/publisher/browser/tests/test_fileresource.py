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
"""

Revision information:
$Id: test_fileresource.py,v 1.8 2003/11/21 17:12:10 jim Exp $
"""

import os

from unittest import TestCase, main, makeSuite

from zope.security.checker import NamesChecker

from zope.exceptions import NotFoundError

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.tests import ztapi
from zope.proxy import removeAllProxies

from zope.i18n.interfaces import IUserPreferredCharsets

from zope.publisher.http import IHTTPRequest
from zope.publisher.http import HTTPCharsets
from zope.publisher.browser import TestRequest

from zope.app.publisher.browser.fileresource import FileResourceFactory
from zope.app.publisher.browser.fileresource import ImageResourceFactory
import zope.app.publisher.browser.tests as p

checker = NamesChecker(
    ('__call__', 'HEAD', 'request', 'publishTraverse', 'GET')
    )

test_directory = os.path.split(p.__file__)[0]

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        ztapi.provideAdapter(IHTTPRequest, IUserPreferredCharsets,
                             HTTPCharsets)

    def testNoTraversal(self):

        path = os.path.join(test_directory, 'testfiles', 'test.txt')
        resource = FileResourceFactory(path, checker)(TestRequest())
        self.assertRaises(NotFoundError,
                          resource.publishTraverse,
                          resource.request,
                          '_testData')

    def testFileGET(self):

        path = os.path.join(test_directory, 'testfiles', 'test.txt')

        resource = FileResourceFactory(path, checker)(TestRequest())
        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = removeAllProxies(resource.request).response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

    def testFileHEAD(self):

        path = os.path.join(test_directory, 'testfiles', 'test.txt')
        resource = FileResourceFactory(path, checker)(TestRequest())

        self.assertEqual(resource.HEAD(), '')

        response = removeAllProxies(resource.request).response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

    def testImageGET(self):

        path = os.path.join(test_directory, 'testfiles', 'test.gif')

        resource = ImageResourceFactory(path, checker)(TestRequest())

        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = removeAllProxies(resource.request).response
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')

    def testImageHEAD(self):

        path = os.path.join(test_directory, 'testfiles', 'test.gif')
        resource = ImageResourceFactory(path, checker)(TestRequest())

        self.assertEqual(resource.HEAD(), '')

        response = removeAllProxies(resource.request).response
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')



def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
