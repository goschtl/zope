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
"""Tests for keyword index.

$Id$
"""
import unittest

from zope.interface import Interface, Attribute, implements
from zope.interface.verify import verifyObject
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.tests import ztapi
from zope.app.hub import \
    ObjectRegisteredHubEvent, ObjectUnregisteredHubEvent, ObjectModifiedHubEvent
from zope.app.index.keyword.index import KeywordCatalogIndex
from zope.app.index.interfaces.keyword import IUIKeywordCatalogIndex

class ISomeInterface(Interface):
    someField = Attribute("")

class ISomeOtherInterface(Interface):
    someField = Attribute("")

class FakeSearchableObject:

    def __init__(self):
        self.words = ['shiny', 'happy', 'people']

    def someMethod(self):
        return ['monkeys']

class SomeAdapter:

    implements(ISomeInterface)

    def __init__(self, context):
        self.context = context
        meth = context.someMethod()
        if type(meth) is not type([]):
            meth = meth.split()
        words = context.words
        if type(words) is not type([]):
            words = words.split()
        self.someField = words+meth

Bruce = u"Bruce"
Sheila = u"Sheila"

class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        ztapi.provideAdapter(None, ISomeInterface, SomeAdapter)
        self.buildFolders()
        self.index = KeywordCatalogIndex('words')
        self.object = FakeSearchableObject()

    def assertPresent(self, value, docid):
        result = self.index.search(value)
        self.assertEqual(len(result), 1)
        self.assertEqual(list(result.keys()), [docid])

    def assertAbsent(self, value):
        self.assertEqual(len(self.index.search(value)), 0)

    def testInterface(self):
        verifyObject(IUIKeywordCatalogIndex, self.index)

    def testGetValue(self):
        idx = KeywordCatalogIndex('words')
        self.assertEqual(idx._getValue(self.object), ['shiny', 'happy', 'people'])
        idx = KeywordCatalogIndex('someMethod')
        self.assertEqual(idx._getValue(self.object), ['monkeys'])
        idx = KeywordCatalogIndex('someField', ISomeInterface)
        self.assertEqual(idx._getValue(self.object),  ['shiny', 'happy', 'people', 'monkeys'])
        idx = KeywordCatalogIndex('nonexistent')
        self.assertEqual(idx._getValue(self.object), None)
        idx = KeywordCatalogIndex('someField', ISomeOtherInterface)
        self.assertEqual(idx._getValue(self.object), None)

    def testNotIndexing(self):
        docid = 1000
        self.object.words = None
        event = ObjectRegisteredHubEvent(None, docid, object=self.object)
        self.index.notify(event)
        self.assertEqual(self.index.documentCount(), 0)

    def testIndexing(self):
        docid = 1000
        self.object.words = ['bananas']
        event = ObjectRegisteredHubEvent(None, docid, object=self.object)
        self.index.notify(event)
        self.assertEqual(self.index.documentCount(), 1)
        event = ObjectModifiedHubEvent(None, docid, object=self.object)
        self.index.notify(event)
        self.assertEqual(self.index.documentCount(), 1)
        event = ObjectUnregisteredHubEvent(None,docid,None,object=self.object)
        self.index.notify(event)
        self.assertEqual(self.index.documentCount(), 0)

def test_suite():
    return unittest.makeSuite(Test)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
