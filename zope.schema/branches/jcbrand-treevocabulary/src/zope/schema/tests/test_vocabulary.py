##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Test of the Vocabulary and related support APIs.
"""
import unittest

from zope.interface.verify import verifyObject
from zope.interface.exceptions import DoesNotImplement
from zope.interface import Interface, implementer

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
        self.assertTrue(vocabulary.getVocabularyRegistry() is r)

    def test_getVocabularyRegistry(self):
        r = vocabulary.getVocabularyRegistry()
        self.assertTrue(interfaces.IVocabularyRegistry.providedBy(r))

    # TODO: still need to test the default implementation

class SampleTerm(object):
    pass

@implementer(interfaces.IVocabulary)
class SampleVocabulary(object):

    def __iter__(self):
        return iter([self.getTerm(x) for x in range(0, 10)])

    def __contains__(self, value):
        return 0 <= value < 10

    def __len__(self):
        return 10

    def getTerm(self, value):
        if value in self:
            t = SampleTerm()
            t.value = value
            t.double = 2 * value
            return t
        raise LookupError("no such value: %r" % value)


class SimpleVocabularyTests(unittest.TestCase):

    list_vocab = vocabulary.SimpleVocabulary.fromValues([1, 2, 3])
    items_vocab = vocabulary.SimpleVocabulary.fromItems(
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

    def test_simple_term_title(self):
        t = vocabulary.SimpleTerm(1)
        verifyObject(interfaces.ITokenizedTerm, t)
        self.assertRaises(DoesNotImplement, verifyObject,
            interfaces.ITitledTokenizedTerm, t)
        self.assertTrue(t.title is None)
        t = vocabulary.SimpleTerm(1, title="Title")
        verifyObject(interfaces.ITokenizedTerm, t)
        verifyObject(interfaces.ITitledTokenizedTerm, t)
        self.assertEqual(t.title, "Title")

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
        self.assertTrue(verifyObject(interfaces.IVocabulary, self.list_vocab))
        self.assertTrue(
            verifyObject(interfaces.IVocabularyTokenized, self.list_vocab))
        self.assertTrue(verifyObject(interfaces.IVocabulary, self.items_vocab))
        self.assertTrue(
            verifyObject(interfaces.IVocabularyTokenized, self.items_vocab))

    def test_addt_interfaces(self):
        class IStupid(Interface):
            pass
        v = vocabulary.SimpleVocabulary.fromValues([1, 2, 3], IStupid)
        self.assertTrue(IStupid.providedBy(v))

    def test_len(self):
        self.assertEqual(len(self.list_vocab), 3)
        self.assertEqual(len(self.items_vocab), 4)

    def test_contains(self):
        for v in (self.list_vocab, self.items_vocab):
            self.assertTrue(1 in v and 2 in v and 3 in v)
            self.assertTrue(5 not in v)

    def test_iter_and_get_term(self):
        for v in (self.list_vocab, self.items_vocab):
            for term in v:
                self.assertTrue(v.getTerm(term.value) is term)
                self.assertTrue(v.getTermByToken(term.token) is term)

    def test_nonunique_tokens(self):
        self.assertRaises(
            ValueError, vocabulary.SimpleVocabulary.fromValues,
            [2, '2'])
        self.assertRaises(
            ValueError, vocabulary.SimpleVocabulary.fromItems, 
            [(1, 'one'), ('1', 'another one')])
        self.assertRaises(
            ValueError, vocabulary.SimpleVocabulary.fromItems,
            [(0, 'one'), (1, 'one')])

    def test_nonunique_token_message(self):
        try:
            vocabulary.SimpleVocabulary.fromValues([2, '2'])
        except ValueError as e:
            self.assertEqual(str(e), "term tokens must be unique: '2'")

    def test_nonunique_token_messages(self):
        try:
            vocabulary.SimpleVocabulary.fromItems([(0, 'one'), (1, 'one')])
        except ValueError as e:
            self.assertEqual(str(e), "term values must be unique: 'one'")

    def test_overriding_createTerm(self):
        class MyTerm(object):
            def __init__(self, value):
                self.value = value
                self.token = repr(value)
                self.nextvalue = value + 1

        class MyVocabulary(vocabulary.SimpleVocabulary):
            def createTerm(cls, value):
                return MyTerm(value)
            createTerm = classmethod(createTerm)

        vocab = MyVocabulary.fromValues([1, 2, 3])
        for term in vocab:
            self.assertEqual(term.value + 1, term.nextvalue)


class TreeVocabularyTests(unittest.TestCase):

    tree_vocab_2 = vocabulary.TreeVocabulary.fromDict(
        { ('regions', 'Regions'): {
                ('aut', 'Austria'): {
                    ('tyr', 'Tyrol'): {
                        ('auss', 'Ausserfern'): {},
                    }
                },
                ('ger', 'Germany'): {
                    ('bav', 'Bavaria'):{}
                },
            }
        })

    tree_vocab_3 = vocabulary.TreeVocabulary.fromDict(
        { ('marketing', 'marketing', 'Marketing'): {
                ('marketing_marketing', 'marketing_marketing', 'Marketing'): {},
                ('marketing_loyalty', 'marketing_loyalty', 'Loyalty'): {},
                ('marketing_sales', 'marketing_sales', 'Sales'): {
                    ('marketing_sales_call_center', 'marketing_sales_call_center', 'Call Center'): {},
                },
            }
        })

    def test_implementation(self):
        for v in [self.tree_vocab_2, self.tree_vocab_3]:
            self.assertTrue(verifyObject(interfaces.IVocabulary, v))
            self.assertTrue(verifyObject(interfaces.IVocabularyTokenized, v))
            self.assertTrue(verifyObject(interfaces.ITreeVocabulary, v))
            self.assertEqual(dict, type(v._terms))

    def test_addt_interfaces(self):
        class IStupid(Interface):
            pass
        v = vocabulary.TreeVocabulary.fromDict({('one', '1'): {}}, IStupid)
        self.assertTrue(IStupid.providedBy(v))

    def test_termpath(self):
        self.assertEqual(
                    self.tree_vocab_2.getTermPath('Bavaria'), 
                    ['Regions', 'Germany', 'Bavaria'])
        self.assertEqual(
                    self.tree_vocab_2.getTermPath('Austria'), 
                    ['Regions', 'Austria'])
        self.assertEqual(
                    self.tree_vocab_2.getTermPath('Ausserfern'), 
                    ['Regions', 'Austria', 'Tyrol', 'Ausserfern'])
        self.assertEqual(
                    self.tree_vocab_2.getTermPath('Non-existent'), 
                    [])
        self.assertEqual(
                    self.tree_vocab_3.getTermPath('marketing_sales_call_center'),
                    ['marketing', 'marketing_sales', 'marketing_sales_call_center'])

    def test_len(self):
        """ len returns the number of all nodes in the dict
        """
        self.assertEqual(len(self.tree_vocab_2), 6)
        self.assertEqual(len(self.tree_vocab_3), 5)

    def test_contains(self):
        self.assertTrue('Regions' in self.tree_vocab_2 and 
                        'Austria' in self.tree_vocab_2 and 
                        'Bavaria' in self.tree_vocab_2)

        self.assertTrue('bav' not in self.tree_vocab_2)
        self.assertTrue('xxx' not in self.tree_vocab_2)

        self.assertTrue('marketing' in self.tree_vocab_3 and 
                        'marketing_sales' in self.tree_vocab_3 and 
                        'marketing_loyalty' in self.tree_vocab_3)

        self.assertTrue('Marketing' not in self.tree_vocab_3)
        self.assertTrue('Call Center' not in self.tree_vocab_3)

    def test_iter_and_get_term(self):
        for v in (self.tree_vocab_2, self.tree_vocab_3):
            for term in v:
                self.assertTrue(v.getTerm(term.value) is term)
                self.assertTrue(v.getTermByToken(term.token) is term)

    def test_nonunique_values(self):
        self.assertRaises(
            ValueError, vocabulary.TreeVocabulary.fromDict,
            { ('one', '1'): {},
              ('two', '1'): {},
            })
        vocabulary.TreeVocabulary.fromDict({
                ('one', '1', 'One'): {},
                ('two', '2', 'One'): {},
            })

    def test_nonunique_value_message(self):
        try:
            vocabulary.TreeVocabulary.fromDict(
            { ('one', '1'): {},
              ('two', '1'): {},
            })
        except ValueError as e:
            self.assertEqual(str(e), "term values must be unique: '1'")

    def test_overriding_createTerm(self):
        class MyTerm(object):
            def __init__(self, value):
                self.value = value
                self.token = repr(value)
                self.nextvalue = value + 1

        class MyVocabulary(vocabulary.TreeVocabulary):
            def createTerm(cls, token, value, title=None):
                return MyTerm(value)
            createTerm = classmethod(createTerm)

        vocab = MyVocabulary.fromDict(
                    {(1, 1):{}, (2, 2):{}, (3, 3):{ (4,4):{} }} )
        for term in vocab:
            self.assertEqual(term.value + 1, term.nextvalue)


def test_suite():
    suite = unittest.makeSuite(RegistryTests)
    suite.addTest(unittest.makeSuite(SimpleVocabularyTests))
    suite.addTest(unittest.makeSuite(TreeVocabularyTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")

