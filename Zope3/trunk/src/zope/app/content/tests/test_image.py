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

$Id: test_image.py,v 1.4 2002/12/30 14:02:59 stevea Exp $
"""

import unittest
from zope.interface.verify import verifyClass

class TestImage(unittest.TestCase):

    def _makeImage(self, *args, **kw):
        from zope.app.content.image import Image
        return Image(*args, **kw)


    def testEmpty(self):
        file = self._makeImage()
        self.assertEqual(file.getContentType(), '')
        self.assertEqual(file.getData(), None)

    def testConstructor(self):
        file = self._makeImage('Data')
        self.assertEqual(file.getContentType(), '')
        self.assertEqual(file.getData(), 'Data')

    def testMutators(self):
        # XXX What's the point of this test? Does it test that data
        # contents override content-type? Or not? If the former, then
        # real image data should be used.

        file = self._makeImage()

        file.setContentType('text/plain')
        self.assertEqual(file.getContentType(), 'text/plain')

        file.setData('Foobar')
        self.assertEqual(file.getData(), 'Foobar')

        file.edit('Blah', 'text/html')
        self.assertEqual(file.getContentType(), 'text/html')
        self.assertEqual(file.getData(), 'Blah')

    def testInterface(self):
        from zope.app.content.image import Image, IImage

        self.failUnless(IImage.isImplementedByInstancesOf(Image))
        self.failUnless(verifyClass(IImage, Image))


class DummyImage:

    def __init__(self, width, height, bytes):
        self.width = width
        self.height = height
        self.bytes = bytes

    def getSize(self):
        return self.bytes

    def getImageSize(self):
        return self.width, self.height


class TestSized(unittest.TestCase):

    def testInterface(self):
        from zope.app.interfaces.size import ISized
        from zope.app.content.image import ImageSized
        self.failUnless(ISized.isImplementedByInstancesOf(ImageSized))
        self.failUnless(verifyClass(ISized, ImageSized))

    def test_zeroSized(self):
        from zope.app.content.image import ImageSized
        s = ImageSized(DummyImage(0, 0, 0))
        self.assertEqual(s.sizeForSorting(), ('byte', 0))
        self.assertEqual(s.sizeForDisplay(), u'0 KB 0x0')


    def test_arbitrarySize(self):
        from zope.app.content.image import ImageSized
        s = ImageSized(DummyImage(34, 56, 78))
        self.assertEqual(s.sizeForSorting(), ('byte', 78))
        self.assertEqual(s.sizeForDisplay(), u'1 KB 34x56')

    def test_unknownSize(self):
        from zope.app.content.image import ImageSized
        s = ImageSized(DummyImage(-1, -1, 23))
        self.assertEqual(s.sizeForSorting(), ('byte', 23))
        self.assertEqual(s.sizeForDisplay(), u'1 KB ?x?')

def test_suite():
    return unittest.TestSuite((unittest.makeSuite(TestImage),
                               unittest.makeSuite(TestSized)
                             ))

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
