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
"""Bug Tests

$Id: test_bug.py,v 1.2 2003/07/28 17:13:48 srichter Exp $
"""
import unittest

from zope.app.container.tests.test_btree import TestBTreeContainer

from bugtracker.tests.placelesssetup import PlacelessSetup
from bugtracker.interfaces import IBug
from bugtracker.bug import Bug

DCkey = "zope.app.dublincore.ZopeDublinCore"

class BugTest(PlacelessSetup, TestBTreeContainer, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)

    def getBug(self):
        bug = Bug()
        bug.__parent__ = self.generateTracker()
        bug.__name__ = id
        return bug

    def makeTestObject(self):
        return Bug()

    def test_Interface(self):
        self.failUnless(IBug.providedBy(self.getBug()))

    def test_title(self):
        bug = self.getBug()
        self.assertEqual(bug.title, u'')
        bug.title = u'Title'
        self.assertEqual(bug.title, u'Title')
        self.assertEqual(bug.__annotations__[DCkey]['Title'], (u'Title',))

    def test_description(self):
        bug = self.getBug()
        self.assertEqual(bug.description, u'')
        bug.description = u'Description'
        self.assertEqual(bug.description, u'Description')
        self.assertEqual(bug.__annotations__[DCkey]['Description'],
                         (u'Description',))

    def test_owners(self):
        bug = self.getBug()
        self.assertEqual(bug.owners, [])
        bug.owners = [u'srichter']
        self.assertEqual(bug.owners, [u'srichter'])

    def test_status(self):
        bug = self.getBug()
        self.assertEqual(bug.status, u'new')
        bug.status = u'open'
        self.assertEqual(bug.status, u'open')

    def test_type(self):
        bug = self.getBug()
        self.assertEqual(bug.type, u'bug')
        bug.type = u'feature'
        self.assertEqual(bug.type, u'feature')

    def test_priority(self):
        bug = self.getBug()
        self.assertEqual(bug.priority, u'normal')
        bug.priority = u'urgent'
        self.assertEqual(bug.priority, u'urgent')

    def test_release(self):
        bug = self.getBug()
        self.assertEqual(bug.release, u'None')
        bug.release = u'zope_x3'
        self.assertEqual(bug.release, u'zope_x3')

    def test_submitter(self):
        bug = self.getBug()
        # Just here to create the annotations
        bug.title = u''
        self.assertEqual(bug.submitter, None)
        bug.__annotations__[DCkey]['Creator'] = ['srichter']
        self.assertEqual(bug.submitter, u'srichter')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(BugTest),
        ))

if __name__ == '__main__':
    unittest.main()
