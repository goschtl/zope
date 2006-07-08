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
"""Bug Tracker Vocabulary Tests

$Id: test_vocabularies.py,v 1.3 2003/07/28 17:13:48 srichter Exp $
"""
import unittest

from zope.interface import classImplements, implements
from zope.schema.interfaces import ITokenizedTerm
from zope.schema.vocabulary import getVocabularyRegistry

from zope.app import zapi
from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.app.container.contained import contained, Contained
from zope.app.security.interfaces import IAuthentication
from zope.app.security.principalregistry import principalRegistry, Principal

from bugtracker.interfaces import IManagableVocabulary
from bugtracker.interfaces import IBugTracker
from bugtracker.tracker import BugTracker
from bugtracker.vocabulary import SimpleTerm
from bugtracker.vocabulary import StatusVocabulary, PriorityVocabulary
from bugtracker.vocabulary import BugTypeVocabulary, ReleaseVocabulary
from bugtracker.vocabulary import UserTerm, UserVocabulary
from bugtracker.vocabulary import ManagableVocabulary
from bugtracker.vocabulary import VocabularyPropertyGetter
from bugtracker.vocabulary import VocabularyPropertySetter
from bugtracker.tests.placelesssetup import Root


class ManagableVocabularyBaseTest(PlacelessSetup):

    def setUp(self):
        PlacelessSetup.setUp(self)
        classImplements(BugTracker, IAttributeAnnotatable)
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                             AttributeAnnotations)

    def getVocabularyClass(self):
        return NotImplemented

    def makeVocabulary(self):
        tracker = BugTracker()
        contained(tracker, Root(), name="tracker")
        vocab = self.getVocabularyClass()(tracker)
        vocab.annotations.obj.__annotations__ = {}
        data = {'1': SimpleTerm('1', u'one'),
                '2': SimpleTerm('2', u'two'),
                '3': SimpleTerm('3', u'three'),
                '4': SimpleTerm('4', u'four')}
        vocab.annotations.obj.__annotations__[vocab.key] = data
        vocab.annotations.obj.__annotations__[vocab.key+'/default'] = '1'
        return vocab

    def test_contains(self):
        vocab = self.makeVocabulary()
        self.assertEqual(vocab.__contains__('2'), True)
        self.assertEqual(vocab.__contains__('6'), False)

    def test_iter(self):
        vocab = self.makeVocabulary()
        self.assertEqual('2' in map(lambda x: x.value, vocab.__iter__()), True)
        self.assertEqual('6' in map(lambda x: x.value, vocab.__iter__()), False)
        self.assertEqual('2' in map(lambda x: x.value, iter(vocab)), True)
        self.assertEqual('6' in map(lambda x: x.value, iter(vocab)), False)

    def test_len(self):
        vocab = self.makeVocabulary()
        self.assertEqual(vocab.__len__(), 4)
        self.assertEqual(len(vocab), 4)

    def test_getQuery(self):
        vocab = self.makeVocabulary()
        self.assertEqual(vocab.getQuery(), None)

    def test_getTerm(self):
        vocab = self.makeVocabulary()
        self.assertEqual(vocab.getTerm('1').value, '1')
        self.assertEqual(vocab.getTerm('1').title, 'one')
        self.assertRaises(KeyError, vocab.getTerm, ('6',))

    def test_getTermByToken(self):
        vocab = self.makeVocabulary()
        self.assertEqual(vocab.getTermByToken('1').value, '1')
        self.assertEqual(vocab.getTermByToken('1').title, 'one')
        self.assertRaises(KeyError, vocab.getTermByToken, ('6',))

    def test_add(self):
        vocab = self.makeVocabulary()
        vocab.add('5', 'five')
        self.assertEqual(vocab.getTerm('5').value, '5')
        self.assertEqual(vocab.getTerm('5').title, 'five')
        vocab.add('6', 'six', True)
        self.assertEqual(vocab.getTerm('6').value, '6')
        self.assertEqual(vocab.getTerm('6').title, 'six')
        self.assertEqual(vocab.default.value, '6')
        self.assertEqual(vocab.default.title, 'six')

    def test_delete(self):
        vocab = self.makeVocabulary()
        vocab.delete('4')
        self.assertRaises(KeyError, vocab.getTerm, ('4',))
        vocab.default = '2'
        self.assertRaises(ValueError, vocab.delete, '2')

    def test_default(self):
        vocab = self.makeVocabulary()
        vocab.default = '4'
        self.assertEqual(vocab.default.value, '4')
        self.assertEqual(vocab.default.title, 'four')
        vocab.default = vocab.getTerm('3')
        self.assertEqual(vocab.default.value, '3')
        self.assertEqual(vocab.default.title, 'three')


class StatusVocabularyTest(ManagableVocabularyBaseTest, unittest.TestCase):

    def getVocabularyClass(self):
        return StatusVocabulary


class PriorityVocabularyTest(ManagableVocabularyBaseTest, unittest.TestCase):

    def getVocabularyClass(self):
        return PriorityVocabulary


class ReleaseVocabularyTest(ManagableVocabularyBaseTest, unittest.TestCase):

    def getVocabularyClass(self):
        return ReleaseVocabulary


class BugTypeVocabularyTest(ManagableVocabularyBaseTest, unittest.TestCase):

    def getVocabularyClass(self):
        return BugTypeVocabulary


class SimpleTermTest(unittest.TestCase):

    def setUp(self):
        self.term = SimpleTerm('foo', 'bar')

    def test_Interface(self):
        self.failUnless(ITokenizedTerm.providedBy(self.term))

    def test_token(self):
        self.assertEqual(self.term.token, 'foo')
        self.assertEqual(self.term.getToken(), 'foo')

    def test_value_title(self):
        self.assertEqual(self.term.value, 'foo')
        self.assertEqual(self.term.title, 'bar')


class UserTermTest(unittest.TestCase):

    def setUp(self):
        principal = Principal('0', 'Stephan', 'blah', 'srichter', 'Nothing')
        self.term = UserTerm(principal)

    def test_Interface(self):
        self.failUnless(ITokenizedTerm.providedBy(self.term))

    def test_token(self):
        self.assertEqual(self.term.token, '0')

    def test_value(self):
        self.assertEqual(self.term.value, '0')

    def test_principal(self):
        self.assertEqual(self.term.principal['id'], '0')
        self.assertEqual(self.term.principal['login'], 'srichter')
        self.assertEqual(self.term.principal['title'], 'Stephan')


class UserVocabularyTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        ztapi.provideUtility(IAuthentication, principalRegistry)
        principalRegistry.definePrincipal(
            '0', 'title0', 'desc0', 'zero', 'pass0')
        principalRegistry.definePrincipal(
            '1', 'title1', 'desc1', 'one', 'pass1')
        principalRegistry.definePrincipal(
            '2', 'title2', 'desc2', 'two', 'pass2')

        self.vocab = UserVocabulary(None)

    def test_contains(self):
        self.assertEqual(self.vocab.__contains__('0'), True)
        self.assertEqual(self.vocab.__contains__('3'), False)

    def test_iter(self):
        vocab = self.vocab
        self.assertEqual('0' in map(lambda x: x.value, vocab.__iter__()), True)
        self.assertEqual('3' in map(lambda x: x.value, vocab.__iter__()), False)
        self.assertEqual('0' in map(lambda x: x.value, iter(vocab)), True)
        self.assertEqual('3' in map(lambda x: x.value, iter(vocab)), False)

    def test_len(self):
        self.assertEqual(self.vocab.__len__(), 3)
        self.assertEqual(len(self.vocab), 3)

    def test_getQuery(self):
        self.assertEqual(self.vocab.getQuery(), None)

    def test_getTerm(self):
        self.assertEqual(self.vocab.getTerm('1').value, '1')
        self.assertEqual(self.vocab.getTerm('1').principal['login'], 'one')
        self.assertRaises(KeyError, self.vocab.getTerm, ('3',))

    def test_getTermByToken(self):
        vocab = self.vocab
        self.assertEqual(vocab.getTermByToken('1').value, '1')
        self.assertEqual(vocab.getTermByToken('1').principal['login'], 'one')
        self.assertRaises(KeyError, vocab.getTermByToken, ('3',))


class SampleVocabulary(ManagableVocabulary):
    key = 'vocab/values'
    interface = IBugTracker
    title = 'Vocabulary'

class SampleObject(Contained):

    sample = property(VocabularyPropertyGetter('_sample', 'Vocabs'),
                      VocabularyPropertySetter('_sample', 'Vocabs'))


class ManagableVocabularyBaseTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        classImplements(BugTracker, IAttributeAnnotatable)
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                             AttributeAnnotations)
        registry = getVocabularyRegistry()
        registry.register('Vocabs', SampleVocabulary)

        tracker = BugTracker()
        contained(tracker, Root(), name="tracker")
        vocab = SampleVocabulary(tracker)
        vocab.annotations.obj.__annotations__ = {}
        data = {'1': SimpleTerm('1', u'one'),
                '2': SimpleTerm('2', u'two'),
                '3': SimpleTerm('3', u'three'),
                '4': SimpleTerm('4', u'four')}
        vocab.annotations.obj.__annotations__[vocab.key] = data
        vocab.annotations.obj.__annotations__[vocab.key+'/default'] = '1'
        self.tracker = tracker

    def getObject(self):
        obj = SampleObject()
        contained(obj, self.tracker, name="1")
        return obj

    def test_getter(self):
        obj = self.getObject()
        self.assertEqual(obj.sample, '1')
        obj._sample = '2'
        self.assertEqual(obj.sample, '2')

    def test_setter(self):
        obj = self.getObject()
        obj.sample = '2'
        self.assertEqual(obj.sample, '2')
        try:
            obj.sample = '7'
            self.failIf(True)
        except ValueError:
            pass


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SimpleTermTest),
        unittest.makeSuite(StatusVocabularyTest),
        unittest.makeSuite(PriorityVocabularyTest),
        unittest.makeSuite(ReleaseVocabularyTest),
        unittest.makeSuite(BugTypeVocabularyTest),
        unittest.makeSuite(UserTermTest),
        unittest.makeSuite(UserVocabularyTest),
        unittest.makeSuite(ManagableVocabularyBaseTest),
        ))

if __name__ == '__main__':
    unittest.main()
