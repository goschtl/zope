##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""I18n Image Tests

$Id$
"""

import unittest
from zope.interface.verify import verifyClass
from zope.i18n.tests.testii18naware import TestII18nAware

from zope.app.i18nfile.i18nimage import I18nImage

def sorted(list):
    list.sort()
    return list

class Test(TestII18nAware):

    def _makeImage(self, *args, **kw):
        return I18nImage(*args, **kw)

    def _createObject(self):
        obj = self._makeImage(defaultLanguage='fr')
        obj.setData('', 'lt')
        obj.setData('', 'en')
        return obj

    def testEmpty(self):
        file = self._makeImage()

        self.assertEqual(file.contentType, '')
        self.assertEqual(file.getData(), '')
        self.assertEqual(file.getDefaultLanguage(), 'en')


    def testConstructor(self):
        file = self._makeImage('Data')
        self.assertEqual(file.contentType, '')
        self.assertEqual(file.getData(), 'Data')
        self.assertEqual(file.getData('en'), 'Data')
        self.assertEqual(file.getData('nonexistent'), 'Data')
        self.assertEqual(file.getDefaultLanguage(), 'en')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en'])

        file = self._makeImage('Data', defaultLanguage='fr')
        self.assertEqual(file.contentType, '')
        self.assertEqual(file.getData(), 'Data')
        self.assertEqual(file.getData('en'), 'Data')
        self.assertEqual(file.getData('nonexistent'), 'Data')
        self.assertEqual(file.getDefaultLanguage(), 'fr')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['fr'])

    def testMutators(self):
        image = self._makeImage()

        # Check that setData updates content type only when updating the
        # default language.  Need some real images or at least headers
        # for that.

        gifHdr = 'GIF87a\x20\x00\x10\x00'
        image.setData(gifHdr)
        self.assertEqual(image.contentType, 'image/gif')

        pngHdr = '\211PNG\r\n\032\n\0\0\0\x20\0\0\0\x10'
        image.setData(pngHdr, 'fr')
        self.assertEqual(image.contentType, 'image/gif')

        image.setData(pngHdr, 'en')
        self.assertEqual(image.contentType, 'image/png')

    def testInterface(self):
        from zope.app.file.interfaces import IImage
        from zope.app.i18nfile.interfaces import II18nFile
        from zope.i18n.interfaces import II18nAware

        self.failUnless(IImage.implementedBy(I18nImage))
        self.failUnless(verifyClass(IImage, I18nImage))

        self.failUnless(II18nAware.implementedBy(I18nImage))
        self.failUnless(verifyClass(II18nAware, I18nImage))

        self.failUnless(II18nFile.implementedBy(I18nImage))
        self.failUnless(verifyClass(II18nFile, I18nImage))

    def testSetDefaultLanguage(self):
        # getDefaultLanguage and getAvailableLanguages are tested in the
        # above tests

        file = self._makeImage()

        file.setData('', language='lt')
        file.setDefaultLanguage('lt')
        self.assertEqual(file.getDefaultLanguage(), 'lt')


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
