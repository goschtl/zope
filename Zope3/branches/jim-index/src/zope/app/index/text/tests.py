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

$Id$
"""

import unittest

from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.traversing.api import traverse
from zope.component import getService
from zope.app.servicenames import HubIds
from zope.app.hub.interfaces import \
     IRegistrationHubEvent, IObjectModifiedHubEvent
from zope.app.hub import \
     ObjectRegisteredHubEvent, ObjectUnregisteredHubEvent, \
     ObjectModifiedHubEvent

from zope.app.index.interfaces.text import ISearchableText
from zope.app.index.text.index import TextIndex
from zope.interface import implements


class FakeSearchableObject:
    implements(ISearchableText)
    def __init__(self):
        self.texts = [u"Bruce"]
    def getSearchableText(self):
        return self.texts

Bruce = u"Bruce"
Sheila = u"Sheila"

class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self, site=True)
        self.index = TextIndex()
        self.rootFolder['myIndex'] = self.index
        self.rootFolder['bruce'] = FakeSearchableObject()
        self.object = self.rootFolder['bruce']

    def assertPresent(self, word, docid):
        results, total = self.index.query(word)
        self.assertEqual(total, 1)
        self.assertEqual(results[0][0], docid)

    def assertAbsent(self, word):
        self.assertEqual(self.index.query(word), ([], 0))


    def testNotIndexing(self):
        docid = 1000
        self.object.texts = None
        event = ObjectRegisteredHubEvent(None, docid, object=self.object)
        self.index.notify(event)
        self.assertEqual(self.index.documentCount(), 0)

    def testHubMachinery(self):
        # Technically this is a functional test
        self.createStandardServices()
        index = traverse(self.rootFolder, '/myIndex')
        hub = getService(self.rootFolder, HubIds)
        
        hub.subscribe(index, IRegistrationHubEvent)
        hub.subscribe(index, IObjectModifiedHubEvent)
        location = "/bruce"

        hubid = hub.register(location)
        self.assertPresent(Bruce, hubid)

        self.object.texts = [Sheila]
        event = ObjectModifiedEvent(self.object)
        hub.notify(event)
        self.assertPresent(Sheila, hubid)
        self.assertAbsent(Bruce)

        hub.unregister(location)
        self.assertAbsent(Bruce)
        self.assertAbsent(Sheila)

    def testBootstrap(self):
        # Need to set up a HubIds service because the standard subscription
        # mix-ins expect to see one.
        self.createStandardServices()
    
        index = traverse(self.rootFolder, '/myIndex')
        self.assertEqual(index.isSubscribed(), False)
        self.assertAbsent(Bruce)
        self.assertAbsent(Sheila)
        location = '/bruce'
        hub = getService(self.rootFolder, HubIds)
        hubid = hub.register(location)
        index.subscribe(hub)
        self.assertEqual(index.isSubscribed(), True)
        self.assertPresent(Bruce, hubid)

        index.unsubscribe(hub)
        self.assertEqual(index.isSubscribed(), False)
        self.assertPresent(Bruce, hubid)

        self.object.texts = [Sheila]
        event = ObjectModifiedEvent(self.object)
        hub.notify(event)
        self.assertPresent(Bruce, hubid)
        self.assertAbsent(Sheila)


def test_suite():
    return unittest.makeSuite(Test)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
