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

"""Test of the VocabularyField and related support APIs."""

import sys
import unittest

from zope.interface.verify import verifyObject
from zope.interface import Interface

from zope.schema import interfaces
from zope.schema import vocabulary


class DummyRegistry(vocabulary.VocabularyRegistry):
    def get(self, object, name):
        v = SampleVocabulary()
        v.object = object
        v.name = name
        return v


class BaseTest(unittest.TestCase):
    # Clear the vocabulary and presentation registries on each side of
    # each test.

    def setUp(self):
        vocabulary._clear()

    def tearDown(self):
        vocabulary._clear()


class RegistryTests(BaseTest):
    """Tests of the simple vocabulary and presentation registries."""

    def test_setVocabularyRegistry(self):
        r = DummyRegistry()
        vocabulary.setVocabularyRegistry(r)
        self.assert_(vocabulary.getVocabularyRegistry() is r)

    def test_getVocabularyRegistry(self):
        r = vocabulary.getVocabularyRegistry()
        self.assert_(interfaces.IVocabularyRegistry.isImplementedBy(r))

    # XXX still need to test the default implementation

class SampleTerm:
    pass

class SampleVocabulary:
    __implements__ = interfaces.IVocabulary

    def __contains__(self, value):
        return 0 <= value < 10

    def __len__(self):
        return 10

    def getQuery(self):
        return None

    def getTerm(self, value):
        if value in self:
            t = SampleTerm()
            t.value = value
            t.double = 2 * value
            return t
        raise LookupError("no such value: %r" % value)


class VocabularyFieldTests(BaseTest):
    """Tests of the VocabularyField implementation."""

    def check_preconstructed(self, cls, okval, badval):
        v = SampleVocabulary()
        field = cls(vocabulary=v)
        self.assert_(field.vocabulary is v)
        self.assert_(field.vocabularyName is None)
        bound = field.bind(None)
        self.assert_(bound.vocabulary is v)
        self.assert_(bound.vocabularyName is None)
        bound.default = okval
        self.assertEqual(bound.default, okval)
        self.assertRaises(interfaces.ValidationError,
                          setattr, bound, "default", badval)

    def test_preconstructed_vocabulary(self):
        self.check_preconstructed(vocabulary.VocabularyField, 1, 42)

    def test_preconstructed_vocabulary_multi(self):
        self.check_preconstructed(vocabulary.VocabularyListField,
                                  [1], [1, 42])

    def check_constructed(self, cls, okval, badval):
        vocabulary.setVocabularyRegistry(DummyRegistry())
        field = cls(vocabulary="vocab")
        self.assert_(field.vocabulary is None)
        self.assertEqual(field.vocabularyName, "vocab")
        o = object()
        bound = field.bind(o)
        self.assert_(isinstance(bound.vocabulary, SampleVocabulary))
        bound.default = okval
        self.assertEqual(bound.default, okval)
        self.assertRaises(interfaces.ValidationError,
                          setattr, bound, "default", badval)

    def test_constructed_vocabulary(self):
        self.check_constructed(vocabulary.VocabularyField, 1, 42)

    def test_constructed_vocabulary_multi(self):
        self.check_constructed(vocabulary.VocabularyListField,
                               [1], [1, 42])

    def test_abstract_base_class_is_abstract(self):
        self.assertRaises(NotImplementedError,
                          vocabulary.VocabularyMultiField, vocabulary="foo")


class SimpleVocabularyTests(unittest.TestCase):
    
    def setUp(self):
        self.list_vocab = vocabulary.SimpleVocabulary([1, 2, 3])
        self.items_vocab = vocabulary.SimpleVocabulary.fromItems(
            [('one', 1), ('two', 2), ('three', 3), ('fore!', 4)])
    
    def test_simple_term(self):
        t = vocabulary.SimpleTerm(1)
        verifyObject(interfaces.ITokenizedTerm, t)
        self.assertEqual(t.value, 1)
        self.assertEqual(t.token, "1")
        t = vocabulary.SimpleTerm(1, "One")
        verifyObject(interfaces.ITokenizedTerm, t)
        self.assertEqual(t.value, 1)
        self.assertEqual(t.token, "One")
        
    def test_order(self):
        value = 1
        for t in self.list_vocab:
            self.assertEqual(t.value, value)
            value += 1
            
        value = 1
        for t in self.items_vocab:
            self.assertEqual(t.value, value)
            value += 1
    
    def test_implementation(self):
        self.failUnless(verifyObject(interfaces.IVocabulary, self.list_vocab))
        self.failUnless(
            verifyObject(interfaces.IVocabularyTokenized, self.list_vocab))
        self.failUnless(verifyObject(interfaces.IVocabulary, self.items_vocab))
        self.failUnless(
            verifyObject(interfaces.IVocabularyTokenized, self.items_vocab))
            
    def test_addt_interfaces(self):
        class IStupid(Interface):
            pass
        v = vocabulary.SimpleVocabulary([1, 2, 3], IStupid)
        self.failUnless(IStupid.isImplementedBy(v))
    
    def test_len(self):
        self.assertEqual(len(self.list_vocab), 3)
        self.assertEqual(len(self.items_vocab), 4)
    
    def test_contains(self):
        for v in (self.list_vocab, self.items_vocab):
            self.assert_(1 in v and 2 in v and 3 in v)
            self.assert_(5 not in v)
            
    def test_get_query(self):
        self.assert_(self.list_vocab.getQuery() is None)
        
    def test_iter_and_get_term(self):
        for v in (self.list_vocab, self.items_vocab):
            for term in v:
                self.assert_(v.getTerm(term.value) is term)
                self.assert_(v.getTermByToken(term.token) is term)
        
    def test_nonunique_tokens(self):
        self.assertRaises(
            AssertionError, vocabulary.SimpleVocabulary, [2, '2'])
        self.assertRaises(
            AssertionError, vocabulary.SimpleVocabulary.fromItems, 
            [(1, 'one'), ('1', 'another one')])
        

def test_suite():
    suite = unittest.makeSuite(RegistryTests)
    suite.addTest(unittest.makeSuite(VocabularyFieldTests))
    suite.addTest(unittest.makeSuite(SimpleVocabularyTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
