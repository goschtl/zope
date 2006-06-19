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
"""Bug Tracker Mail Subscription and Mailer Tests

$Id$
"""
import unittest

from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.app.container.tests.test_btree import TestBTreeContainer

from bugtracker.tests.placelesssetup import PlacelessSetup
from bugtracker.interfaces import IBugTracker
from bugtracker.tracker import BugTracker
from bugtracker.bug import Bug


class TrackerTest(PlacelessSetup, TestBTreeContainer, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)

    def makeTestObject(self):
        return BugTracker()

    def test_Interface(self):
        self.failUnless(IBugTracker.providedBy(self.makeTestObject()))

    def test_title(self):
        tracker = self.makeTestObject()
        self.assertEqual(tracker.title, u'')
        tracker.title = u'test'
        self.assertEqual(tracker.title, u'test')
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TrackerTest),
        ))

if __name__ == '__main__':
    unittest.main()
