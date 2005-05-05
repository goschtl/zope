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
"""XML Export/Import Tests

$Id: test_xmlexportimport.py,v 1.4 2003/07/28 17:13:48 srichter Exp $
"""
import unittest, os
from datetime import datetime

from zope.app.file import File
from zope.app.datetimeutils import parseDatetimetz
from zope.app.dublincore.interfaces import IZopeDublinCore

from bugtracker import tests
from bugtracker.bug import Bug, BugDependencyAdapter
from bugtracker.exportimport import XMLExport, XMLImport
from bugtracker.interfaces import IBug, IBugDependencies
from bugtracker.tests.placelesssetup import PlacelessSetup, Root
from bugtracker.tracker import BugTracker


class ImportTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        tracker = BugTracker()
        tracker.__parent__ = Root()
        tracker.__name__ = 'tracker'
        file = os.path.join(os.path.split(tests.__file__)[0], 'tracker.xml')
        XMLImport(tracker).processXML(open(file))
        self.tracker = tracker

    def test_properties(self):
        tracker = self.tracker
        self.assertEqual(tracker.title, u'Bug Tracker')

    def test_bug(self):
        bug = self.tracker['1']
        self.assertEqual(bug.title, u'Bug 1')
        self.assertEqual(bug.submitter, u'anybody')
        self.assertEqual(bug.status, u'new')
        self.assertEqual(bug.priority, u'urgent')
        self.assertEqual(bug.type, u'bug')
        self.assertEqual(bug.release, u'None')
        bug.owners.sort()
        self.assertEqual(bug.owners, [u'zope.jim', u'zope.srichter'])
        dc = IZopeDublinCore(bug)
        self.assertEqual(dc.created, parseDatetimetz(u'2003-01-01T23:00:00'))
        self.assertEqual(dc.modified, parseDatetimetz(u'2003-01-02T23:00:00'))
        self.assertEqual(bug.description, u'This is Bug 1.')
        self.assertEqual(bug.description.ttype, u'zope.source.stx')

    def test_comment(self):
        comment = self.tracker['1']['comment1']
        dc = IZopeDublinCore(comment)
        self.assertEqual(dc.created, parseDatetimetz(u'2003-01-01T13:00:00'))
        self.assertEqual(dc.creators[0], u'zope.srichter')
        self.assertEqual(comment.body, u'This is a comment.')
        self.assertEqual(comment.body.ttype, u'zope.source.rest')

    def test_attach(self):
        attach = self.tracker['1']['document.gif']
        dc = IZopeDublinCore(attach)
        self.assertEqual(dc.created, parseDatetimetz(u'2003-01-01T14:00:00'))
        self.assertEqual(dc.creators[0], u'zope.srichter')
        # Type was set to 'File'
        self.assert_(isinstance(attach, File))


class ExportTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        tracker = BugTracker()
        tracker.__parent__ = Root()
        tracker.__name__ = 'tracker'
        file = os.path.join(os.path.split(tests.__file__)[0], 'tracker.xml')
        XMLImport(tracker).processXML(open(file))
        self.xml = XMLExport(tracker).getXML()

    def test_bugtracker(self):
        self.assert_('<bugtracker version="1.0" title="Bug Tracker">' in
                     self.xml)

    def test_vocabulary(self):
        self.assert_('<vocabulary name="Stati">' in self.xml)
        self.assert_('<term value="closed" title="Closed"/>' in self.xml)
        self.assert_('<term value="new" title="New" default=""/>' in self.xml)
        self.assert_('<vocabulary name="Priorities">' in self.xml)
        self.assert_('<term value="urgent" title="Urgent"/>' in self.xml)
        self.assert_('<term value="low" title="Low" default=""/>' in self.xml)
        self.assert_('<vocabulary name="BugTypes">' in self.xml)
        self.assert_('<term value="bug" title="Bug" default=""/>' in self.xml)
        self.assert_('<vocabulary name="Releases">' in self.xml)
        self.assert_(
          '<term value="None" title="(not specified)" default=""/>' in self.xml)

    def test_bug(self):
        self.assert_('id="1"' in self.xml)
        self.assert_('title="Bug 1"' in self.xml)
        self.assert_('submitter="anybody"' in self.xml)
        self.assert_('status="new"' in self.xml)
        self.assert_('priority="urgent"' in self.xml)
        self.assert_('type="bug"' in self.xml)
        self.assert_('release="None' in self.xml)
        self.assert_('owners="jim, srichter' in self.xml or
                     'owners="srichter, jim' in self.xml)
        self.assert_('dependencies=""' in self.xml)
        self.assert_('created="Jan 1, 2003 11:00:00 PM"' in self.xml)
        self.assert_('modified="Jan 2, 2003 11:00:00 PM"' in self.xml)
        self.assert_('<description ttype="zope.source.stx">'
                     '\nThis is Bug 1.\n      '
                     '</description>' in self.xml)

    def test_comment(self):
        self.assert_('id="comment1"' in self.xml)
        self.assert_('created="Jan 1, 2003 1:00:00 PM"' in self.xml)
        self.assert_('creator="srichter"' in self.xml)
        self.assert_('ttype="zope.source.rest"' in self.xml)
        self.assert_('>\nThis is a comment.\n        </comment>' in self.xml)

    def test_attachment(self):
        self.assert_('id="document.gif"' in self.xml)
        self.assert_('created="Jan 1, 2003 2:00:00 PM"' in self.xml)
        self.assert_('creator="srichter"' in self.xml)
        self.assert_('type="File"' in self.xml)
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ImportTest),
        unittest.makeSuite(ExportTest),
        ))

if __name__ == '__main__':
    unittest.main()
