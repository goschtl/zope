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
"""Tests for text index.

$Id: test_index.py,v 1.3 2002/12/04 14:22:59 gvanrossum Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter
from Zope.Event.ObjectEvent import ObjectModifiedEvent

from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup import \
     PlacefulSetup

from Zope.App.Traversing.ITraverser import ITraverser
from Zope.App.Traversing import locationAsUnicode

from Zope.App.OFS.Services.ObjectHub.IHubEvent import \
     IRegistrationHubEvent, IObjectModifiedHubEvent
from Zope.App.OFS.Services.ObjectHub.HubEvent import \
     ObjectRegisteredHubEvent, \
     ObjectUnregisteredHubEvent, \
     ObjectModifiedHubEvent
from Zope.App.OFS.Services.ObjectHub.ObjectHub import ObjectHub

from Zope.App.index.text.interfaces import ISearchableText
from Zope.App.index.text.index import TextIndex

class FakeSearchableObject:
    __implements__ = ISearchableText
    def __init__(self):
        self.texts = [u"Bruce"]
    def getSearchableText(self):
        return self.texts

class FakeTraverser:
    __implements__ = ITraverser
    def __init__(self, object, location):
        self.__object = object
        self.__location = location
    def traverse(self, path):
        canonical_path = locationAsUnicode(path)
        if canonical_path == self.__location:
            return self.__object
        raise KeyError, (path, canonical_path)

class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.index = TextIndex()
        self.object = FakeSearchableObject()

    def testNotification(self):
        event = ObjectRegisteredHubEvent(None, 1000, object=self.object)
        self.index.notify(event)
        results, total = self.index.query(u"Bruce")
        self.assertEqual(total, 1)
        self.assertEqual(results[0][0], 1000)

        self.object.texts = [u"Sheila"]
        event = ObjectModifiedHubEvent(None, 1000, object=self.object)
        self.index.notify(event)
        self.assertEqual(self.index.query(u"Bruce"), ([], 0))
        results, total = self.index.query(u"Sheila")
        self.assertEqual(total, 1)
        self.assertEqual(results[0][0], 1000)

        event = ObjectUnregisteredHubEvent(None, 1000,
                                           location="fake",
                                           object=self.object)
        self.index.notify(event)
        self.assertEqual(self.index.query(u"Bruce"), ([], 0))
        self.assertEqual(self.index.query(u"Sheila"), ([], 0))

    def testHubMachinery(self):
        # Technically this is a functional test
        hub = ObjectHub()
        hub.subscribe(self.index, IRegistrationHubEvent)
        hub.subscribe(self.index, IObjectModifiedHubEvent)
        location = "/bruce"
        traverser = FakeTraverser(self.object, location)
        provideAdapter(None, ITraverser, lambda dummy: traverser)

        hubid = hub.register(location)
        results, total = self.index.query(u"Bruce")
        self.assertEqual(total, 1)
        self.assertEqual(results[0][0], hubid)

        self.object.texts = [u"Sheila"]
        event = ObjectModifiedEvent(self.object, location)
        hub.notify(event)
        self.assertEqual(self.index.query(u"Bruce"), ([], 0))
        results, total = self.index.query(u"Sheila")
        self.assertEqual(total, 1)
        self.assertEqual(results[0][0], hubid)

        hub.unregister(location)
        self.assertEqual(self.index.query(u"Bruce"), ([], 0))
        self.assertEqual(self.index.query(u"Sheila"), ([], 0))

    def testBootstrap(self):
        hub = ObjectHub()
        location = "/bruce"
        traverser = FakeTraverser(self.object, location)
        provideAdapter(None, ITraverser, lambda dummy: traverser)
        hubid = hub.register(location)
        self.index.subscribe(hub)
        results, total = self.index.query(u"Bruce")
        self.assertEqual(total, 1)
        self.assertEqual(results[0][0], hubid)

        self.index.unsubscribe(hub)
        results, total = self.index.query(u"Bruce")
        self.assertEqual(total, 1)
        self.assertEqual(results[0][0], hubid)

        self.object.texts = [u"Sheila"]
        event = ObjectModifiedEvent(self.object, location)
        hub.notify(event)
        results, total = self.index.query(u"Bruce")
        self.assertEqual(total, 1)
        self.assertEqual(results[0][0], hubid)
        self.assertEqual(self.index.query(u"Sheila"), ([], 0))

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
