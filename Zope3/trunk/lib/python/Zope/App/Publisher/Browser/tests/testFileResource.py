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
$Id: testFileResource.py,v 1.5 2002/10/04 18:37:23 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

import os

from Zope.Exceptions import NotFoundError

from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalResourceService import provideResource
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter

from Zope.I18n.IUserPreferredCharsets import IUserPreferredCharsets

from Zope.Publisher.HTTP.HTTPRequest import IHTTPRequest
from Zope.Publisher.HTTP.HTTPCharsets import HTTPCharsets
from Zope.Publisher.Browser.BrowserRequest import TestRequest

from Zope.App.Publisher.Browser.FileResource import FileResourceFactory
from Zope.App.Publisher.Browser.FileResource import ImageResourceFactory
import Zope.App.Publisher.Browser.tests as p        

test_directory = os.path.split(p.__file__)[0]


class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)    

    def testNoTraversal(self):

        path = os.path.join(test_directory, 'test.txt')
        resource = FileResourceFactory(path)(TestRequest())

        self.assertRaises(NotFoundError,
                          resource.publishTraverse,
                          resource.request,
                          '_testData')

    def testFileGET(self):

        path = os.path.join(test_directory, 'test.txt')

        resource = FileResourceFactory(path)(TestRequest())

        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

    def testFileHEAD(self):

        path = os.path.join(test_directory, 'test.txt')
        resource = FileResourceFactory(path)(TestRequest())

        self.assertEqual(resource.HEAD(), '')

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

    def testImageGET(self):

        path = os.path.join(test_directory, 'test.gif')

        resource = ImageResourceFactory(path)(TestRequest())

        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')

    def testImageHEAD(self):

        path = os.path.join(test_directory, 'test.gif')
        resource = ImageResourceFactory(path)(TestRequest())

        self.assertEqual(resource.HEAD(), '')

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')
                         
        

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
