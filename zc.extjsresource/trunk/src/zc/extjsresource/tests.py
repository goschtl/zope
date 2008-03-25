##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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
import os, unittest
from zope.testing import doctest

import zope.component
import zope.interface

from zope.app.publisher.browser.tests import test_directoryresource
DirectoryResourceFactory_orig = test_directoryresource.DirectoryResourceFactory

import zc.extjsresource

class FauxExtjsResource:

    def __init__(self, request):
        pass

    def __call__(self):
        return 'http://localhost/@@/extjs'

class Test(test_directoryresource.Test):

    def setUp(self):
        test_directoryresource.Test.setUp(self)
        test_directoryresource.DirectoryResourceFactory = (
            zc.extjsresource.DirectoryResourceFactory)

    def tearDown(self):
        test_directoryresource.DirectoryResourceFactory = (
            DirectoryResourceFactory_orig)
        test_directoryresource.Test.tearDown(self)

    def test_set_blank_image_js(self):
        path = os.path.join(test_directoryresource.test_directory, 'testfiles')
        request = test_directoryresource.TestRequest()
        factory = zc.extjsresource.DirectoryResourceFactory(
            path, test_directoryresource.checker, 'testfiles')
        resource = factory(request)

        zope.component.provideAdapter(
            FauxExtjsResource,
            [test_directoryresource.TestRequest],
            zope.interface.Interface, 'extjs',
            )

        self.assertEqual(
            resource.publishTraverse(request, 'set_blank_image.js')(),
            "Ext.BLANK_IMAGE_URL = "
            "'http://localhost/@@/extjs/resources/images/default/s.gif';\n"
            )

def test_suite():
    return unittest.makeSuite(Test)
