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

$Id: test_index.py,v 1.1 2002/12/04 11:10:24 gvanrossum Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Zope.App.index.text.interfaces import ISearchableText
from Zope.App.index.text.index import TextIndex

from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup import \
     PlacefulSetup

from Zope.App.OFS.Services.ObjectHub.HubEvent import \
     ObjectRegisteredHubEvent, \
     ObjectUnregisteredHubEvent, \
     ObjectModifiedHubEvent

class FakeSearchableObject:
    __implements__ = ISearchableText
    def __init__(self):
        self.texts = [u"Bruce"]
    def getSearchableText(self):
        return self.texts

class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.index = TextIndex()
        self.object = FakeSearchableObject()

    def testEverything(self):
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

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
