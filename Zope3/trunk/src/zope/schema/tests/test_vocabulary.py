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
        self.check_preconstructed(vocabulary.VocabularyMultiField,
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
        self.check_constructed(vocabulary.VocabularyMultiField,
                               [1], [1, 42])


def test_suite():
    suite = unittest.makeSuite(RegistryTests)
    suite.addTest(unittest.makeSuite(VocabularyFieldTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
