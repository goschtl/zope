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
"""Unit tests for the Photo class

$Id: test_photo.py,v 1.3 2003/11/21 22:07:36 BjornT Exp $
"""

import unittest

from zope.app.container.sample import SampleContainer
from zope.app.container.tests.test_icontainer import BaseTestIContainer
from zope.app.container.tests.test_icontainer import DefaultTestData
from zope.app.file.tests.test_image import zptlogo
from zope.app.file.image import Image
from zope.app.dublincore.interfaces import ICMFDublinCore
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.interface import implements
from zope.interface.verify import verifyObject
from zope.app import zapi
from zope.app.tests import ztapi

from photo.interfaces import IPhoto, IPhotoContainer
from photo.interfaces import IImageResizeUtility
from photo import Photo, defaultImageResizer

small_image = Image(zptlogo)

class ImageResizeStub:
    implements(IImageResizeUtility)

    def resize(self, image, size, keep_aspect=True):
        return small_image

class PhotoContainer(SampleContainer):
    implements(IPhotoContainer)

    currentDisplayId = 'small'
    resizeUtility = defaultImageResizer

class DublinCoreStub:
    def __call__(self, photo):
        return self

    title = ''
    description = ''

dublinCoreStub = DublinCoreStub()

class TestPhoto(PlacefulSetup, BaseTestIContainer, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        ztapi.provideAdapter(IPhoto, ICMFDublinCore, dublinCoreStub)
        us = zapi.getService('Utilities', self)
        us.provideUtility(IImageResizeUtility, ImageResizeStub(),
                          defaultImageResizer) 

    def makeTestObject(self):
        return Photo()

    def getUnknownKey(self):
        return 'm'

    def getBadKeyTypes(self):
        return [None, ['foo'], 1, '\xf3abc']

    def makeTestData(self):
        return DefaultTestData()

    def _makePhotoInsidePc(self):
        self.createRootFolder()
        pc = PhotoContainer()
        pc['a'] = Photo()
        self.rootFolder['pc'] = pc
        photo = zapi.traverseName(pc, 'a')
        return photo
        
    def test_interface(self):
        photo = self._makePhotoInsidePc()
        verifyObject(IPhoto, photo)


    def test_title(self):
        photo = Photo()
        self.assertEqual(u'', photo.title)
        photo.title = u'A Title'
        self.assertEqual(u'A Title', photo.title)


    def test_data(self):
        photo = Photo()
        self.assertEqual(photo.data, '')
        photo.data = zptlogo
        self.assertEqual(photo.data, zptlogo)


    def test_currentDisplayId(self):
        photo = self._makePhotoInsidePc()
        photo.useParentOptions = False
        photo.currentDisplayId = 'original'
        self.assertEqual(photo.currentDisplayId, 'original')

        photo.currentDisplayId = 'not a display id'
        self.assertEqual(photo.currentDisplayId, 'original')

        photo.useParentOptions = True
        self.assertEqual(photo.currentDisplayId, 'small')

    def test_description(self):
        photo = Photo()
        self.assertEqual(u'', photo.description)
        photo.description = u'A Description'
        self.assertEqual(u'A Description', photo.description)


    def test_getDisplayIds(self):
        photo = Photo()
        self.assert_('thumbnail' in photo.getDisplayIds())
        photo = Photo()
        photo.data = zptlogo
        self.assert_('original' in photo.getDisplayIds())


    def test_getImage(self):
        photo = self._makePhotoInsidePc()
        photo.data = zptlogo
        org = photo.getImage('original')
        self.assertEqual(org.data, zptlogo)
        self.assertEqual(photo.getImage('not a display id'), None)

        im = photo.getImage('small')
        self.assertEqual(small_image.getImageSize(), im.getImageSize())


    def test_getDisplaySize(self):
        photo = Photo()
        photo.data = zptlogo
        im = Image(zptlogo)
        self.assertEqual(photo.getDisplaySize('original'), im.getImageSize())
        self.assertEqual(photo.getDisplaySize('not a display id'), None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPhoto))
    return suite


if __name__ == '__main__':
    unittest.main()
