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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_imageupload.py,v 1.3 2002/12/30 14:02:52 stevea Exp $
"""

import os
import unittest

import zope.app.content # __file__

from zope.app.browser.content.image import ImageUpload
from zope.app.browser.form.editview import EditView
from zope.app.browser.form.widget import BytesWidget, BytesAreaWidget
from zope.app.content.image import Image, IImage
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.view import provideView, setDefaultViewName
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.schema.interfaces import IField, IBytesLine, IBytes


class IU(ImageUpload, EditView):
    schema = IImage


class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)

        # Configure the widget views
        setDefaultViewName(IField, IBrowserPresentation, 'edit')
        provideView(IBytesLine, 'edit', IBrowserPresentation, BytesWidget)
        provideView(IBytes, 'edit', IBrowserPresentation, BytesAreaWidget)

        icondir = os.path.split(zope.app.browser.content.__file__)[0]
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
