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
$Id: testFileResource.py,v 1.1 2002/06/13 23:15:44 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

import os
from Zope.Exceptions import NotFoundError
from Zope.Publisher.Browser.BrowserRequest import TestRequest
import Zope.App.Publisher.Browser.tests as p        
test_directory = os.path.split(p.__file__)[0]
from Zope.App.Publisher.Browser.FileResource import FileResourceFactory
from Zope.App.Publisher.Browser.FileResource import ImageResourceFactory

class Test(TestCase):

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

        response = resource.request.getResponse()
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

    def testFileHEAD(self):

        path = os.path.join(test_directory, 'test.txt')
        resource = FileResourceFactory(path)(TestRequest())

        self.assertEqual(resource.HEAD(), '')

        response = resource.request.getResponse()
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

    def testImageGET(self):

        path = os.path.join(test_directory, 'test.gif')

        resource = ImageResourceFactory(path)(TestRequest())

        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = resource.request.getResponse()
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')

    def testImageHEAD(self):

        path = os.path.join(test_directory, 'test.gif')
        resource = ImageResourceFactory(path)(TestRequest())

        self.assertEqual(resource.HEAD(), '')

        response = resource.request.getResponse()
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')
                         
        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
