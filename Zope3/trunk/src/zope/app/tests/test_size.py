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
import unittest

from zope.app.interfaces.size import ISized

class DummyObject:

    def __init__(self, size):
        self._size = size

    def getSize(self):
        return self._size

class Test(unittest.TestCase):

    def testImplementsISized(self):
        from zope.app.size import DefaultSized
        sized = DefaultSized(object())
        self.assert_(ISized.isImplementedBy(sized))

    def testSizeWithBytes(self):
        from zope.app.size import DefaultSized
        obj = DummyObject(1023)
        sized = DefaultSized(obj)
        self.assertEqual(sized.sizeForSorting(), ('byte', 1023))
        self.assertEqual(sized.sizeForDisplay(), u'1 KB')

    def testSizeWithNone(self):
        from zope.app.size import DefaultSized
        obj = DummyObject(None)
        sized = DefaultSized(obj)
        self.assertEqual(sized.sizeForSorting(), (None, None))
        self.assertEqual(sized.sizeForDisplay(), u'n/a')

    def testSizeNotAvailable(self):
        from zope.app.size import DefaultSized
        sized = DefaultSized(object())
        self.assertEqual(sized.sizeForSorting(), (None, None))
        self.assertEqual(sized.sizeForDisplay(), u'n/a')

    def testVariousSizes(self):
        from zope.app.size import DefaultSized

        sized = DefaultSized(DummyObject(0))
        self.assertEqual(sized.sizeForSorting(), ('byte', 0))
        self.assertEqual(sized.sizeForDisplay(), u'0 KB')

        sized = DefaultSized(DummyObject(1))
        self.assertEqual(sized.sizeForSorting(), ('byte', 1))
        self.assertEqual(sized.sizeForDisplay(), u'1 KB')

        sized = DefaultSized(DummyObject(2048))
        self.assertEqual(sized.sizeForSorting(), ('byte', 2048))
        self.assertEqual(sized.sizeForDisplay(), u'2 KB')

        sized = DefaultSized(DummyObject(2000000))
        self.assertEqual(sized.sizeForSorting(), ('byte', 2000000))
        self.assertEqual(sized.sizeForDisplay(), u'1.91 MB')

    def test_byteDisplay(self):
        from zope.app.size import byteDisplay
        self.assertEqual(byteDisplay(0), u'0 KB')
        self.assertEqual(byteDisplay(1), u'1 KB')
        self.assertEqual(byteDisplay(2048), u'2 KB')
        self.assertEqual(byteDisplay(2000000), u'1.91 MB')

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
