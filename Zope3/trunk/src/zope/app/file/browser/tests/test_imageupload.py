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
"""Image Upload Test

$Id: test_imageupload.py,v 1.6 2004/03/17 17:37:03 philikon Exp $
"""

import os
import unittest

from zope.app.tests import ztapi
from zope.app.form.browser.editview import EditView
from zope.app.form.browser import BytesWidget, BytesAreaWidget
from zope.app.form.interfaces import IInputWidget
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.publisher.browser import TestRequest
from zope.schema.interfaces import IField, IBytesLine, IBytes

import zope.app.file.browser # for __file__
from zope.app.file.image import Image, IImage
from zope.app.file.browser.image import ImageUpload


class IU(ImageUpload, EditView):
    schema = IImage


class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()

        # Configure the widget views
        ztapi.browserViewProviding(IBytesLine, BytesWidget, IInputWidget)
        ztapi.browserViewProviding(IBytes, BytesAreaWidget, IInputWidget)

        icondir = os.path.split(zope.app.file.browser.__file__)[0]
        data = open(os.path.join(icondir, 'image_icon.gif'), 'rb').read()
        image = Image(data)
        self.__view = IU(image, TestRequest())

    def test_size(self):
        self.assertEqual(self.__view.size(), "16 x 16 pixels, 1 KB")

    def test_apply_update_no_data(self):
        view = self.__view
        ct = view.context.contentType
        data = view.context.data
        d = {}
        self.failUnless(view.apply_update(d))
        self.assertEqual(view.context.contentType, ct)
        self.assertEqual(view.context.data, data)
        d = {'contentType': 'image/gif'}
        self.failUnless(view.apply_update(d))
        self.assertEqual(view.context.contentType, ct)
        self.assertEqual(view.context.data, data)

    def test_apply_update_new_contentType(self):
        view = self.__view
        view.context.contentType = 'foo/bar'
        self.assertEqual(view.context.contentType, 'foo/bar')
        data = view.context.data
        d = {'contentType': 'xxx/yyy'}
        self.failIf(view.apply_update(d))
        self.assertEqual(view.context.contentType, 'xxx/yyy')
        self.assertEqual(view.context.data, data)

    def test_apply_update_new_data(self):
        view = self.__view
        gifdata = view.context.data
        view.context.contentType = 'foo/bar'
        view.context.data = ''
        ct = view.context.contentType
        self.assertEqual(ct, 'foo/bar')
        data = view.context.data
        self.assertEqual(data, '')
        d = {'data': gifdata}
        self.failIf(view.apply_update(d))
        self.assertEqual(view.context.contentType, 'image/gif')
        self.assertEqual(view.context.data, gifdata)

    def test_apply_update_new_data_and_new_ct(self):
        view = self.__view
        gifdata = view.context.data
        view.context.contentType = 'foo/bar'
        view.context.data = ''
        ct = view.context.contentType
        self.assertEqual(ct, 'foo/bar')
        data = view.context.data
        self.assertEqual(data, '')
        d = {'contentType': 'xxx/yyy', 'data': gifdata}
        self.failIf(view.apply_update(d))
        self.assertEqual(view.context.contentType, 'image/gif')
        self.assertEqual(view.context.data, gifdata)


def test_suite():
    return unittest.makeSuite(Test)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
