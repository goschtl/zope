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

from unittest import TestCase, TestSuite, main, makeSuite

from zodb.btrees.IIBTree import IISet
from zope.fieldindex.fieldindex import FieldIndex
from zope.fieldindex.ifieldindex import IFieldIndex
from zope.interface.verify import verifyClass

class FieldIndexTest(TestCase):

    def setUp(self):
        self.index = FieldIndex()

    def _populate_index(self):

        self.index.index_doc(1, 'the')
        self.index.index_doc(2, 'quick')
        self.index.index_doc(3, 'brown')
        self.index.index_doc(4, 'fox')
        self.index.index_doc(5, 'fox')

    def _search(self, value, expected):

        results = self.index.search(value)

        # results and expected are IISets() but we can not
        # compare them directly since __eq__() does not seem
        # to be implemented for BTrees

        self.assertEqual(results.keys(), expected.keys())


    def test_interface(self):
        verifyClass(IFieldIndex, FieldIndex)


    def test_empty_index(self):
        self.assertEqual(self.index.documentCount(), 0)

        self._populate_index()
        self.assertEqual(self.index.documentCount(), 5)

        self.index.clear()
        self.assertEqual(self.index.documentCount(), 0)


    def test_hasdoc(self):
    
        self._populate_index()
        self.assertEqual(self.index.has_doc(1), 1)
        self.assertEqual(self.index.has_doc(2), 1)
        self.assertEqual(self.index.has_doc(3), 1)
        self.assertEqual(self.index.has_doc(4), 1)
        self.assertEqual(self.index.has_doc(5), 1)
        self.assertEqual(self.index.has_doc(99), 0)



    def test_indexdoc(self):

        self._populate_index()

        self._search('the', IISet([1]))
        self._search('quick', IISet([2]))
        self._search('brown', IISet([3]))
        self._search('fox', IISet([4,5]))
        self._search('sucks', IISet([]))


    def test_unindexdoc(self):

        self._populate_index()

        self.index.unindex_doc(99999)       # not exisiting
        self.assertEqual(self.index.documentCount(), 5)

        self.index.unindex_doc(3)
        self.index.unindex_doc(4)
        self.assertEqual(self.index.documentCount(), 3)


def test_suite():
    return TestSuite((makeSuite(FieldIndexTest), ))

if __name__=='__main__':
    main(defaultTest='test_suite')
