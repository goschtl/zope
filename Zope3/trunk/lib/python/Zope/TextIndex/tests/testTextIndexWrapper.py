##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Unit tests for TextIndexWrapper.

$Id: testTextIndexWrapper.py,v 1.1 2002/12/03 16:45:23 gvanrossum Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Zope.TextIndex.TextIndexWrapper import TextIndexWrapper

class Test(TestCase):

    def setUp(self):
        w = TextIndexWrapper()
        doc1 = u"the quick brown fox jumps over the lazy dog"
        doc2 = u"the brown fox and the yellow fox don't need the retriever"
        w.index_doc(1000, [doc1])
        w.index_doc(1001, [doc2])
        self.wrapper = w

    def testOne(self):
        matches, total = self.wrapper.query(u"quick fox", 0, 10)
        self.assertEqual(total, 1)
        [(docid, rank)] = matches # if this fails there's a problem
        self.assertEqual(docid, 1000)

    def testNone(self):
        matches, total = self.wrapper.query(u"dalmatian", 0, 10)
        self.assertEqual(total, 0)
        self.assertEqual(len(matches), 0)

    def testAll(self):
        matches, total = self.wrapper.query(u"brown fox", 0, 10)
        self.assertEqual(total, 2)
        self.assertEqual(len(matches), 2)
        matches.sort()
        self.assertEqual(matches[0][0], 1000)
        self.assertEqual(matches[1][0], 1001)

    def testBatching(self):
        matches1, total = self.wrapper.query(u"brown fox", 0, 1)
        self.assertEqual(total, 2)
        self.assertEqual(len(matches1), 1)
        matches2, total = self.wrapper.query(u"brown fox", 1, 1)
        self.assertEqual(total, 2)
        self.assertEqual(len(matches2), 1)
        matches = matches1 + matches2
        matches.sort()
        self.assertEqual(matches[0][0], 1000)
        self.assertEqual(matches[1][0], 1001)

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
