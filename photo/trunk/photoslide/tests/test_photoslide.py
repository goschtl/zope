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
"""Tests for the PhotoSlide class

$Id: test_photoslide.py,v 1.3 2003/11/21 22:12:02 BjornT Exp $
"""

import unittest

from zope.app.container.tests.test_icontainer import BaseTestIContainer
from zope.app.container.tests.test_icontainer import DefaultTestData
from zope.app.file.tests.test_image import zptlogo
from zope.app.file.image import Image
from zope.interface.verify import verifyObject

small_image = Image(zptlogo)

class TestPhotoSlide(BaseTestIContainer, unittest.TestCase):

    def makeTestObject(self):
        from photoslide import PhotoSlide
        return PhotoSlide()

    def getUnknownKey(self):
        return 'm'
    
    def getBadKeyTypes(self):
        return [None, ['foo'], 1, '\xf3abc']

    def makeTestData(self):
        return DefaultTestData()

    def test_interface(self):
        from photoslide.interfaces import IPhotoSlide
        from photoslide import PhotoSlide

        verifyObject(IPhotoSlide, PhotoSlide())

    def test_title(self):
        from photoslide import PhotoSlide

        photoslide = PhotoSlide()
        self.assertEqual(u'', photoslide.title)
        photoslide.title = u'A Title'
        self.assertEqual(u'A Title', photoslide.title)

    def test_description(self):
        from photoslide import PhotoSlide

        photoslide = PhotoSlide()
        self.assertEqual(u'', photoslide.description)
        photoslide.description = u'A Description'
        self.assertEqual(u'A Description', photoslide.description)

    def test_positions(self):
        from photoslide import PhotoSlide
        from photo import Photo

        photoSlide = PhotoSlide()
        aPhoto = Photo()
        anotherPhoto = Photo()
        yetAnotherPhoto = Photo()
        photoSlide['a'] = aPhoto
        photoSlide['b'] = anotherPhoto
        photoSlide['c'] = yetAnotherPhoto
        self.assertEqual(photoSlide.getPosition('a'), 1)
        self.assertEqual(photoSlide.getPosition('b'), 2)
        self.assertEqual(photoSlide.getPosition('c'), 3)
        self.assertEqual(photoSlide.getPhotos()[0], aPhoto)
        self.assertEqual(photoSlide.getPhotos()[1], anotherPhoto)
        self.assertEqual(photoSlide.getPhotos()[2], yetAnotherPhoto)
        self.assertEqual(photoSlide.getPhotoNames()[0], 'a')
        self.assertEqual(photoSlide.getPhotoNames()[1], 'b')
        self.assertEqual(photoSlide.getPhotoNames()[2], 'c')

        photoSlide.setPosition('a', 3)
        self.assertEqual(photoSlide.getPosition('a'), 3)
        self.assertEqual(photoSlide.getPosition('b'), 1)
        self.assertEqual(photoSlide.getPosition('c'), 2)
        self.assertEqual(photoSlide.getPhotos()[2], aPhoto)
        self.assertEqual(photoSlide.getPhotos()[0], anotherPhoto)
        self.assertEqual(photoSlide.getPhotos()[1], yetAnotherPhoto)
        self.assertEqual(photoSlide.getPhotoNames()[2], 'a')
        self.assertEqual(photoSlide.getPhotoNames()[0], 'b')
        self.assertEqual(photoSlide.getPhotoNames()[1], 'c')

        photoSlide.setPosition('a', 2)
        self.assertEqual(photoSlide.getPosition('a'), 2)
        self.assertEqual(photoSlide.getPosition('b'), 1)
        self.assertEqual(photoSlide.getPosition('c'), 3)
        self.assertEqual(photoSlide.getPhotos()[1], aPhoto)
        self.assertEqual(photoSlide.getPhotos()[0], anotherPhoto)
        self.assertEqual(photoSlide.getPhotos()[2], yetAnotherPhoto)
        self.assertEqual(photoSlide.getPhotoNames()[1], 'a')
        self.assertEqual(photoSlide.getPhotoNames()[0], 'b')
        self.assertEqual(photoSlide.getPhotoNames()[2], 'c')



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPhotoSlide))
    return suite


if __name__ == '__main__':
    unittest.main()
