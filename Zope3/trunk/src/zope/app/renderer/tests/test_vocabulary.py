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

$Id: test_vocabulary.py,v 1.3 2004/03/02 14:24:45 srichter Exp $
"""
import unittest

from zope.app import zapi
from zope.app.renderer import SourceFactory
from zope.app.renderer.interfaces import ISource
from zope.app.renderer.vocabulary import SourceTypeTerm, SourceTypeVocabulary
from zope.component.factory import FactoryInfo
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.schema.interfaces import \
     ITokenizedTerm, IVocabulary, IVocabularyTokenized


class IFoo(ISource):
    """Source marker interface"""

FooFactory = SourceFactory(IFoo)

class IFoo2(ISource):
    """Source marker interface"""

Foo2Factory = SourceFactory(IFoo2)



class SourceTypeTermTest(unittest.TestCase):

    def setUp(self):
        self.term = SourceTypeTerm('zope.Foo', FactoryInfo('Foo', 'Foo Source'))

    def test_Interface(self):
        self.failUnless(ITokenizedTerm.isImplementedBy(self.term))

    def test_token(self):
        self.assertEqual(self.term.token, 'zope.Foo')

    def test_value(self):
        self.assertEqual(self.term.value, 'zope.Foo')


class SourceTypeVocabularyTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(SourceTypeVocabularyTest, self).setUp()
        
        factories = zapi.getService(None, 'Factories')
        factories.provideFactory('zope.source.Foo', FooFactory,
                                 FactoryInfo('Foo', 'Foo Source'))
        factories.provideFactory('zope.source.Foo2', Foo2Factory,
                                 FactoryInfo('Foo2', 'Foo2 Source'))

        self.vocab = SourceTypeVocabulary(None)

    def test_Interface(self):
        self.failUnless(IVocabulary.isImplementedBy(self.vocab))
        self.failUnless(IVocabularyTokenized.isImplementedBy(self.vocab))

    def test_contains(self):
        self.assertEqual(self.vocab.__contains__('zope.source.Foo'), True)
        self.assertEqual(self.vocab.__contains__('zope.source.Foo3'), False)

    def test_iter(self):
        self.assertEqual(
            'zope.source.Foo' in [term.value for term in iter(self.vocab)],
            True)
        self.assertEqual(
            'zope.source.Foo3' in [term.value for term in iter(self.vocab)],
            False)

    def test_len(self):
        self.assertEqual(self.vocab.__len__(), 2)
        self.assertEqual(len(self.vocab), 2)

    def test_getQuery(self):
        self.assertEqual(self.vocab.getQuery(), None)

    def test_getTerm(self):
        self.assertEqual(self.vocab.getTerm('zope.source.Foo').title, 'Foo')
        self.assertRaises(KeyError, self.vocab.getTerm, ('zope.source.Foo3',))

    def test_getTermByToken(self):
        vocab = self.vocab
        self.assertEqual(vocab.getTermByToken('zope.source.Foo').title, 'Foo')
        self.assertRaises(KeyError, vocab.getTermByToken, ('zope.source.Foo3',))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SourceTypeTermTest),
        unittest.makeSuite(SourceTypeVocabularyTest),
        ))

if __name__ == '__main__':
    unittest.main()
