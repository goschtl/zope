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
"""Tests for Global Wiki Source Type Service.

$Id: test_vocabulary.py,v 1.2 2003/11/27 13:59:24 philikon Exp $
"""
import unittest

from zope.app.interfaces.renderer import IGlobalSourceTypeService
from zope.app.renderer.sourcetype import SourceTypes
from zope.app.renderer.vocabulary import SourceTypeTerm, SourceTypeVocabulary
from zope.component.service import defineService, serviceManager
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.interface import Interface, implements
from zope.schema.interfaces import \
     ITokenizedTerm, IVocabulary, IVocabularyTokenized



class IFoo(Interface):
    pass

class Foo:
    implements(IFoo)

class IFoo2(Interface):
    pass

class Foo2:
    implements(IFoo2)


class SourceTypeTermTest(unittest.TestCase):

    def setUp(self):
        self.term = SourceTypeTerm('Foo')

    def test_Interface(self):
        self.failUnless(ITokenizedTerm.isImplementedBy(self.term))

    def test_token(self):
        self.assertEqual(self.term.token, 'Foo')

    def test_value(self):
        self.assertEqual(self.term.value, 'Foo')


class SourceTypeVocabularyTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(SourceTypeVocabularyTest, self).setUp()
        defineService("SourceTypeRegistry", IGlobalSourceTypeService)
        serviceManager.provideService("SourceTypeRegistry", SourceTypes)
        SourceTypes._clear()
        SourceTypes.provide('Foo', IFoo, Foo)
        SourceTypes.provide('Foo 2', IFoo2, Foo2)
        self.vocab = SourceTypeVocabulary(None)

    def test_Interface(self):
        self.failUnless(IVocabulary.isImplementedBy(self.vocab))
        self.failUnless(IVocabularyTokenized.isImplementedBy(self.vocab))

    def test_contains(self):
        self.assertEqual(self.vocab.__contains__('Foo'), True)
        self.assertEqual(self.vocab.__contains__('Foo 3'), False)

    def test_iter(self):
        vocab = self.vocab
        self.assertEqual('Foo' in map(lambda x: x.value, vocab.__iter__()),
                         True)
        self.assertEqual('Foo 3' in map(lambda x: x.value, vocab.__iter__()),
                         False)
        self.assertEqual('Foo' in map(lambda x: x.value, iter(vocab)),
                         True)
        self.assertEqual('Foo 3' in map(lambda x: x.value, iter(vocab)),
                         False)

    def test_len(self):
        self.assertEqual(self.vocab.__len__(), 2)
        self.assertEqual(len(self.vocab), 2)

    def test_getQuery(self):
        self.assertEqual(self.vocab.getQuery(), None)

    def test_getTerm(self):
        self.assertEqual(self.vocab.getTerm('Foo').value, 'Foo')
        self.assertRaises(KeyError, self.vocab.getTerm, ('Foo 3',))

    def test_getTermByToken(self):
        vocab = self.vocab
        self.assertEqual(vocab.getTermByToken('Foo').value, 'Foo')
        self.assertRaises(KeyError, vocab.getTermByToken, ('Foo 3',))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SourceTypeTermTest),
        unittest.makeSuite(SourceTypeVocabularyTest),
        ))

if __name__ == '__main__':
    unittest.main()
