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

$Id: testi18nfile.py,v 1.3 2002/12/31 02:51:57 jim Exp $
"""

import unittest
from zope.interface.verify import verifyClass
from zope.app.content.file import FileChunk
from zope.i18n.tests.testii18naware import TestII18nAware


def sorted(list):
    list.sort()
    return list


class Test(TestII18nAware):


    def _makeFile(self, *args, **kw):
        """ """
        from zope.app.content.i18nfile import I18nFile

        return I18nFile(*args, **kw)


    def _createObject(self):
        obj = self._makeFile(defaultLanguage='fr')
        obj.setData('', 'lt')
        obj.setData('', 'en')
        return obj


    def testEmpty(self):

        file = self._makeFile()

        self.assertEqual(file.getContentType(), '')
        self.assertEqual(file.getData(), '')
        self.assertEqual(file.getDefaultLanguage(), 'en')


    def testConstructor(self):

        file = self._makeFile('Foobar')
        self.assertEqual(file.getContentType(), '')
        self.assertEqual(file.getData(), 'Foobar')
        self.assertEqual(file.getData('en'), 'Foobar')
        self.assertEqual(file.getData('nonexistent'), 'Foobar')
        self.assertEqual(file.getDefaultLanguage(), 'en')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en'])


        file = self._makeFile('Foobar', 'text/plain')
        self.assertEqual(file.getContentType(), 'text/plain')
        self.assertEqual(file.getData(), 'Foobar')
        self.assertEqual(file.getData('en'), 'Foobar')
        self.assertEqual(file.getData('nonexistent'), 'Foobar')
        self.assertEqual(file.getDefaultLanguage(), 'en')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en'])


        file = self._makeFile(data='Foobar', contentType='text/plain')
        self.assertEqual(file.getContentType(), 'text/plain')
        self.assertEqual(file.getData(), 'Foobar')
        self.assertEqual(file.getData('en'), 'Foobar')
        self.assertEqual(file.getData('nonexistent'), 'Foobar')
        self.assertEqual(file.getDefaultLanguage(), 'en')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en'])


        file = self._makeFile(data='Foobar', contentType='text/plain',
                              defaultLanguage='fr')
        self.assertEqual(file.getContentType(), 'text/plain')
        self.assertEqual(file.getData(), 'Foobar')
        self.assertEqual(file.getData('en'), 'Foobar')
        self.assertEqual(file.getData('nonexistent'), 'Foobar')
        self.assertEqual(file.getDefaultLanguage(), 'fr')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['fr'])


    def testMutators(self):

        file = self._makeFile()

        file.setContentType('text/plain')
        self.assertEqual(file.getContentType(), 'text/plain')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en'])

        file.setData('Foobar')
        self.assertEqual(file.getData(), 'Foobar')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en'])

        file.setData('Barbaz', language='fr')
        self.assertEqual(file.getData(), 'Foobar')
        self.assertEqual(file.getData('fr'), 'Barbaz')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en', 'fr'])

        file.edit('Blah', 'text/html')
        self.assertEqual(file.getContentType(), 'text/html')
        self.assertEqual(file.getData(), 'Blah')
        self.assertEqual(file.getData('fr'), 'Barbaz')
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en', 'fr'])

        file.edit('Quux', 'text/html', 'lt')
        self.assertEqual(file.getContentType(), 'text/html')
        self.assertEqual(file.getData(), 'Blah')
        self.assertEqual(file.getData('fr'), 'Barbaz')
        self.assertEqual(file.getData('lt'), 'Quux')
        self.assertEqual(file.getSize(), len('Blah'))
        self.assertEqual(file.getSize('fr'), len('Barbaz'))
        self.assertEqual(file.getSize('lt'), len('Quux'))
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en', 'fr', 'lt'])

        file.removeLanguage('lt')
        self.assertEqual(file.getContentType(), 'text/html')
        self.assertEqual(file.getData(), 'Blah')
        self.assertEqual(file.getData('fr'), 'Barbaz')
        self.assertEqual(file.getSize(), len('Blah'))
        self.assertEqual(file.getSize('fr'), len('Barbaz'))
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en', 'fr'])
        self.assertEqual(file.getData('lt'), 'Blah')
        self.assertEqual(file.getSize('lt'), len('Blah'))

        file.removeLanguage('nonexistent')
        self.assertEqual(file.getContentType(), 'text/html')
        self.assertEqual(file.getData(), 'Blah')
        self.assertEqual(file.getData('fr'), 'Barbaz')
        self.assertEqual(file.getSize(), len('Blah'))
        self.assertEqual(file.getSize('fr'), len('Barbaz'))
        self.assertEqual(sorted(file.getAvailableLanguages()), ['en', 'fr'])
        self.assertEqual(file.getData('lt'), 'Blah')
        self.assertEqual(file.getSize('lt'), len('Blah'))

        self.assertRaises(ValueError, file.removeLanguage, file.getDefaultLanguage())

        self.assertRaises(ValueError, file.setDefaultLanguage, 'nonexistent')


    def testLargeDataInput(self):

        file = self._makeFile()

        # Insert as string
        file.setData('Foobar'*60000, 'en')
        self.assertEqual(file.getSize('en'), 6*60000)
        self.assertEqual(file.getData('en'), 'Foobar'*60000)

        # Insert data as FileChunk
        fc = FileChunk('Foobar'*4000)
        file.setData(fc, 'lt')
        self.assertEqual(file.getSize('lt'), 6*4000)
        self.assertEqual(file.getData('lt'), 'Foobar'*4000)

        # Insert data from file object
        import cStringIO
        sio = cStringIO.StringIO()
        sio.write('Foobar'*100000)
        sio.seek(0)
        file.setData(sio, 'fr')
        self.assertEqual(file.getSize('fr'), 6*100000)
        self.assertEqual(file.getData('fr'), 'Foobar'*100000)


    def testInterface(self):

        from zope.app.interfaces.content.file import IFile
        from zope.app.interfaces.content.i18nfile import II18nFile
        from zope.app.content.i18nfile import I18nFile
        from zope.i18n.interfaces import II18nAware

        self.failUnless(IFile.isImplementedByInstancesOf(I18nFile))
        self.failUnless(verifyClass(IFile, I18nFile))

        self.failUnless(II18nAware.isImplementedByInstancesOf(I18nFile))
        self.failUnless(verifyClass(II18nAware, I18nFile))

        self.failUnless(II18nFile.isImplementedByInstancesOf(I18nFile))
        self.failUnless(verifyClass(II18nFile, I18nFile))


    def testSetDefaultLanguage(self):

        # getDefaultLanguage and getAvailableLanguages are tested in the
        # above tests

        file = self._makeFile()

        file.setData('', language='lt')
        file.setDefaultLanguage('lt')
        self.assertEqual(file.getDefaultLanguage(), 'lt')


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )
