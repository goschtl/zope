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
"""Unit tests for PhotoSized

$Id: test_size.py,v 1.2 2003/09/21 22:17:48 BjornT Exp $
"""

import unittest

from zope.app.file.tests.test_image import zptlogo
from zope.app.site.tests.placefulsetup import PlacefulSetup
from photo import Photo, PhotoSized

class TestPhotoSized(PlacefulSetup, unittest.TestCase):
    def test_sizeForSorting(self):
        size = PhotoSized(Photo())
        self.assertEqual(size.sizeForSorting(), ('byte', 0))

        photo = Photo()
        photo.data = zptlogo
        size = PhotoSized(photo)
        self.assertEqual(size.sizeForSorting(),
                         ('byte', photo.getImage('original').getSize()))

    def test_sizeForDisplay(self):
        size = PhotoSized(Photo())
        self.assertEqual(size.sizeForDisplay(), "")

        photo = Photo()
        photo.data = zptlogo
        x, y = photo.getImage('original').getImageSize()
        imsize = photo.getImage('original').getSize()
        size = PhotoSized(photo)
        self.assertEqual(size.sizeForDisplay(),
                         '${size} ${unit} ${x}x${y}')
        self.assertEqual(size.sizeForDisplay().mapping,
                         {'size': imsize, 'unit': 'bytes',
                          'x': x, 'y': y})
                         


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPhotoSized))
    return suite


if __name__ == '__main__':
    unittest.main()
