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

$Id: testi18nimage.py,v 1.2 2002/12/25 14:12:48 jim Exp $
"""

import unittest
from zope.interface.verify import verifyClass
from zope.i18n.tests.testii18naware import TestII18nAware


def sorted(list):
    list.sort()
    return list


class Test(TestII18nAware):


    def _makeImage(self, *args, **kw):
        """ """
        from zope.app.content.i18nimage import I18nImage

        return I18nImage(*args, **kw)


    def _createObject(self):
        obj = self._makeImage(defaultLanguage='fr')
        obj.setData('', 'lt')
        obj.setData('', 'en')
        return obj


    def testEmpty( self ):

        file = self._makeImage()

        self.assertEqual(file.getContentType(), '')
        self.assertEqual(file.getData(), '')
        self.assertEqual(file.getDefaultLanguage(), 'en')


    def testConstructor(self):

        file = self._makeImage('Data')
        self.assertEqual(file.getContentType(), '')
        self.assertEqual(file.getData(), 'Data')
        self.assertEqual(file.getData('en'), 'Data')
        self.assertEqual(file.getData('nonexistent'), 'Data')
        self.assertEqual(file.getDefaultLanguage(), 'en')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en'])

        file = self._makeImage('Data', defaultLanguage='fr')
        self.assertEqual(file.getContentType(), '')
        self.assertEqual(file.getData(), 'Data')
        self.assertEqual(file.getData('en'), 'Data')
        self.assertEqual(file.getData('nonexistent'), 'Data')
        self.assertEqual(file.getDefaultLanguage(), 'fr')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['fr'])


    def testMutators(self):

        # XXX What's the point of this test? Does it test that data
        # contents override content-type? Or not? If the former, then
        # real image data should be used.

        file = self._makeImage()

        file.setContentType('text/plain')
        self.assertEqual(file.getContentType(), 'text/plain')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en'])

        file.setData('Foobar')
        self.assertEqual(file.getData(), 'Foobar')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en'])

        file.edit('Blah', 'text/html')
        self.assertEqual(file.getContentType(), 'text/html')
        self.assertEqual(file.getData(), 'Blah')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en'])

        file.setData('Foobar in lt', 'lt')
        self.assertEqual(file.getData(), 'Blah')
        self.assertEqual(file.getData('lt'), 'Foobar in lt')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en', 'lt'])

        file.edit('Blah in fr', 'text/html', 'fr')
        self.assertEqual(file.getContentType(), 'text/html')
        self.assertEqual(file.getData(), 'Blah')
        self.assertEqual(file.getData('lt'), 'Foobar in lt')
        self.assertEqual(file.getData('fr'), 'Blah in fr')
        self.assertEqual(sorted(file.getAvailableLanguages()),
                         ['en', 'fr', 'lt'])

        file.removeLanguage('lt')
        self.assertEqual(file.getContentType(), 'text/html')
        self.assertEqual(file.getData(), 'Blah')
        self.assertEqual(file.getData('fr'), 'Blah in fr')
        self.assertEqual(file.getSize(), len('Blah'))
        self.assertEqual(file.getSize('fr'), len('Blah in fr'))
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en', 'fr'])
        self.assertEqual(file.getData('lt'), 'Blah')
        self.assertEqual(file.getSize('lt'), len('Blah'))

        file.removeLanguage('nonexistent')
        self.assertEqual(file.getContentType(), 'text/html')
        self.assertEqual(file.getData(), 'Blah')
        self.assertEqual(file.getData('fr'), 'Blah in fr')
        self.assertEqual(file.getSize(), len('Blah'))
        self.assertEqual(file.getSize('fr'), len('Blah in fr'))
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en', 'fr'])
        self.assertEqual(file.getData('lt'), 'Blah')
        self.assertEqual(file.getSize('lt'), len('Blah'))

        self.assertRaises(ValueError, file.removeLanguage,
                          file.getDefaultLanguage())

        self.assertRaises(ValueError, file.setDefaultLanguage, 'nonexistent')

        # Check that setData updates content type only when updating the
        # default language.  Need some real images or at least headers
        # for that.

        gifHdr = 'GIF87a\x20\x00\x10\x00'
        file.setData(gifHdr)
        self.assertEqual(file.getContentType(), 'image/gif')

        pngHdr = '\211PNG\r\n\032\n\0\0\0\x20\0\0\0\x10'
        file.setData(pngHdr, 'fr')
        self.assertEqual(file.getContentType(), 'image/gif')

        file.setData(pngHdr, 'en')
        self.assertEqual(file.getContentType(), 'image/png')


    def testInterface(self):

        from zope.app.content.image import IImage
        from zope.app.content.i18nimage import I18nImage
        from zope.app.interfaces.content.i18nfile import II18nFile
        from zope.interfaces.i18n import II18nAware

        self.failUnless(IImage.isImplementedByInstancesOf(I18nImage))
        self.failUnless(verifyClass(IImage, I18nImage))

        self.failUnless(II18nAware.isImplementedByInstancesOf(I18nImage))
        self.failUnless(verifyClass(II18nAware, I18nImage))

        self.failUnless(II18nFile.isImplementedByInstancesOf(I18nImage))
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
    return loader.loadTestsFromTestCase( Test )

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )
