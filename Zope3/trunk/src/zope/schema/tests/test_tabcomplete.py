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

"""Tests of the 'tab completion' example vocabulary."""

import unittest

from zope.schema.interfaces import ITerm
from zope.schema.tests import tabcomplete


class TabCompletionTests(unittest.TestCase):

    def setUp(self):
        self.vocab = tabcomplete.CompletionVocabulary(['abc', 'def'])

    def test_successful_query(self):
        subset = self.vocab.queryForPrefix("a")
        L = [term.value for term in subset]
        self.assertEqual(L, ["abc"])
        self.assert_(subset.getMasterVocabulary() is self.vocab)
        subset = self.vocab.queryForPrefix("def")
        L = [term.value for term in subset]
        self.assertEqual(L, ["def"])
        self.assert_(subset.getMasterVocabulary() is self.vocab)

    def test_failed_query(self):
        self.assertRaises(LookupError, self.vocab.queryForPrefix, "g")

    def test_getTerm(self):
        term = self.vocab.getTerm("abc")
        self.assert_(ITerm.isImplementedBy(term))
        self.assertEqual(term.value, "abc")


def test_suite():
    return unittest.makeSuite(TabCompletionTests)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
