##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for ldapauth vocabulary

$Id$
"""
import unittest

from ldapauth.vocabulary import SearchScopeVocabulary
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.schema.interfaces import \
     ITokenizedTerm, IVocabulary, IVocabularyTokenized



class SearchScopeVocabularyTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(SearchScopeVocabularyTest, self).setUp()
        self.vocab = SearchScopeVocabulary(None)

    def test_Interface(self):
        self.failUnless(IVocabulary.providedBy(self.vocab))
        self.failUnless(IVocabularyTokenized.providedBy(self.vocab))

    def test_contains(self):
        self.failUnless(None in self.vocab)
        self.failUnless(0 in self.vocab)
        self.failUnless(1 in self.vocab)
        self.failUnless(2 in self.vocab)
        self.failIf('' in self.vocab)
        self.failIf('base' in self.vocab)
        self.failIf('one' in self.vocab)
        self.failIf('sub' in self.vocab)

    def test_iter(self):
        self.failUnless(None in [term.value for term in self.vocab])
        self.failUnless(0 in [term.value for term in self.vocab])
        self.failUnless(1 in [term.value for term in self.vocab])
        self.failUnless(2 in [term.value for term in self.vocab])
        self.failIf('' in [term.value for term in iter(self.vocab)])
        self.failIf('one' in [term.value for term in iter(self.vocab)])
        self.failIf('base' in [term.value for term in iter(self.vocab)])
        self.failIf('sub' in [term.value for term in iter(self.vocab)])

    def test_len(self):
        self.assertEqual(len(self.vocab), 4)

    def test_getQuery(self):
        self.assertEqual(self.vocab.getQuery(), None)

    def test_getTerm(self):
        self.assertEqual(self.vocab.getTerm(None).title, '')
        self.assertEqual(self.vocab.getTerm(0).title, 'base')
        self.assertEqual(self.vocab.getTerm(1).title, 'one')
        self.assertEqual(self.vocab.getTerm(2).title, 'sub')
        self.assertRaises(
            LookupError, self.vocab.getTerm, ('base',))

    def test_getTermByToken(self):
        vocab = self.vocab
        self.assertEqual(vocab.getTermByToken('None').title, '')
        self.assertEqual(vocab.getTermByToken('0').title, 'base')
        self.assertEqual(vocab.getTermByToken('1').title, 'one')
        self.assertEqual(vocab.getTermByToken('2').title, 'sub')
        self.assertRaises(
            LookupError, vocab.getTermByToken, (None,))
        self.assertRaises(
            LookupError, vocab.getTermByToken, ('base',))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SearchScopeVocabularyTest),
        ))

if __name__ == '__main__':
    unittest.main()
