##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Unit tests for IImageResizeUtility

Use TestIImageResizeUtility as a base class if writing a test for a class
which implements IImageResizeUtility.

Define a function _makeImageResizer(self) which creates the
ImageResizeUtility object.
"""

import unittest

from zope.app.file.image import Image
from zope.app.file.tests.test_image import zptlogo
from zope.interface.verify import verifyObject

from photo.interfaces import IImageResizeUtility

testImage = Image(zptlogo)

class TestIImageResizeUtility(unittest.TestCase):

    def test_implementation(self):
        im_resizer = self._makeImageResizer()
        verifyObject(IImageResizeUtility, im_resizer)

    def test_resizeDontKeepAspect(self):
        im_resizer = self._makeImageResizer()
        image = im_resizer.resize(testImage, (30, 40), False)
        self.assertEqual(image.getImageSize(), (30, 40))
        image = im_resizer.resize(testImage, (40, 30), False)
        self.assertEqual(image.getImageSize(), (40, 30))

    def test_resizeKeepAspect(self):
        im_resizer = self._makeImageResizer()
        image = im_resizer.resize(testImage, (30, 40), True)
        self.assertEqual(image.getImageSize(), (30, 30))
        image = im_resizer.resize(testImage, (40, 30), True)
        self.assertEqual(image.getImageSize(), (30, 30))

def test_suite():
    return unittest.TestSuite() # Deliberately empty

