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

from zope.publisher.browser import TestRequest
from bugtracker.browser.bug import BugBaseView, Overview
from bugtracker.tests.placelesssetup import PlacelessSetup

class BugBaseViewTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(BugBaseViewTest, self).setUp()
        self.view = BugBaseView()
        self.view.context = self.generateBug()
        self.view.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})

    def test_created(self):
        self.assertEqual(self.view.created, '3/3/03 3:00 AM')

    def test_modified(self):
        self.assertEqual(self.view.modified, '3/3/03 4:00 AM')

    def test_description(self):
        self.assertEqual(self.view.description, 'This is Bug 1.')

    def test_status(self):
        self.assertEqual(self.view.status.value, 'new')
        self.assertEqual(self.view.status.title, 'New')

    def test_type(self):
        self.assertEqual(self.view.type.value, 'bug')
        self.assertEqual(self.view.type.title, 'Bug')

    def test_priority(self):
        self.assertEqual(self.view.priority.value, 'normal')
        self.assertEqual(self.view.priority.title, 'Normal')

    def test_release(self):
        self.assertEqual(self.view.release.value, 'None')
        self.assertEqual(self.view.release.title, '(not specified)')

    def test_owners(self):
        self.assertEqual(self.view.owners[0]['login'], 'jim')
        self.assertEqual(self.view.owners[0]['title'], 'Jim Fulton')
        self.assertEqual(self.view.owners[1]['login'], 'stevea')
        self.assertEqual(self.view.owners[1]['title'], 'Steve Alexander')


class OverviewTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.view = Overview()
        self.view.context = self.generateBug()
        self.view.request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})

    def test_comments(self):
        comments = self.view.comments()
        self.assertEqual(comments[0].creator()['id'], u'zope.srichter')
        self.assertEqual(comments[0].modified(), '3/3/03 6:00 AM')
        self.assertEqual(comments[0].body(), 'This is comment 1.')

    def test_attachments(self):
        attachments = self.view.attachments()
        self.assertEqual(attachments[0]['name'], 'attach.txt')
        self.assertEqual(attachments[0]['size'], '1 KB')

    def test_dependencies(self):
        self.assertEqual(self.view.dependencies(), ())


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(BugBaseViewTest),
        unittest.makeSuite(OverviewTest),
        ))

if __name__ == '__main__':
    unittest.main()
