##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""XML-RPC Representation Tests

$Id: test_xmlrpc.py,v 1.4 2003/07/28 20:38:38 srichter Exp $
"""
import unittest
import base64

from zope.publisher.xmlrpc import TestRequest

from zope.app.container.interfaces import IContainer
from zope.app.file import File

from bugtracker.bug import Bug
from bugtracker.comment import Comment
from bugtracker.tracker import BugTracker
from bugtracker.tests.placelesssetup import PlacelessSetup, Root
from bugtracker.xmlrpc import BugTrackerMethods, BugMethods
from bugtracker.xmlrpc import CommentMethods, AttachmentMethods


class TrackerMethodsTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)

        tracker = self.generateTracker()
        tracker.__parent__ = Root()
        tracker.__name__ = "tracker"
        tracker['1'] = self.generateBug('1')
        tracker['2'] = self.generateBug('2')
        self.tracker = tracker
        self.methods = BugTrackerMethods(tracker, TestRequest())

    def test_getBugNames(self):
        self.assertEqual(list(self.methods.getBugNames()), ['1', '2'])

    def test_addBug(self):
        self.methods.addBug(u'Bug 3', u'This is bug 3.')
        self.assertEqual(self.tracker['3'].title, u'Bug 3')
        self.assertEqual(self.tracker['3'].description, u'This is bug 3.')
        self.assertEqual(self.tracker['3'].status, u'new')
        self.methods.addBug(u'Bug 4', u'This is bug 4.', owners=[u'jim'],
                            dependencies=['3'])
        self.assertEqual(self.tracker['4'].dependencies, [u'3'])
        self.assertEqual(self.tracker['4'].owners, [u'zope.jim'])

    def test_deleteBug(self):
        self.methods.deleteBug('2')
        self.assertEqual(list(self.tracker), ['1'])


class BugMethodsTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.bug = self.generateBug('3')
        self.methods = BugMethods(self.bug, TestRequest())

    def test_getProperties(self):
        props = self.methods.getProperties()
        self.assertEqual(props['title'], 'Bug 3')
        self.assertEqual(props['description'], 'This is Bug 3.')
        self.assertEqual(props['type'], 'bug')
        self.assertEqual(props['status'], 'new')
        self.assertEqual(props['priority'], 'normal')
        self.assertEqual(props['release'], 'None')
        self.assertEqual(props['dependencies'], ())
        self.assertEqual(props['owners'], ['jim', 'stevea'])

    def test_setProperties(self):
        self.methods.setProperties(type='feature')
        self.assertEqual(self.bug.type, 'feature')
        self.assertEqual(self.bug.status, 'new')
        self.methods.setProperties(status='closed', release='zope_x3')
        self.assertEqual(self.bug.type, 'feature')
        self.assertEqual(self.bug.status, 'closed')
        self.assertEqual(self.bug.release, 'zope_x3')
        
    def test_getCommentNames(self):
        self.assertEqual(self.methods.getCommentNames(), ['comment1'])

    def test_addComment(self):
        self.methods.addComment('This is comment 2.')
        self.assertEqual(self.bug['comment2'].body, 'This is comment 2.')

    def test_deleteComment(self):
        self.methods.deleteComment('comment1')
        self.assert_('comment1' not in self.bug.keys())

    def test_addAttachment(self):
        self.methods.addAttachment('hw.txt',
                                   base64.encodestring('Hello World.'))
        self.assertEqual(self.bug['hw.txt'].data, 'Hello World.')

    def test_deleteAttachment(self):
        self.methods.deleteAttachment('attach.txt')
        self.assert_('attach.txt' not in self.bug.keys())


class CommentMethodsTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.comment = Comment()
        self.comment.body = 'Comment 1'
        self.methods = CommentMethods(self.comment, TestRequest())

    def test_getBody(self):
        self.assertEqual(self.methods.getBody(), 'Comment 1')

    def test_setBody(self):
        self.methods.setBody('C1')
        self.assertEqual(self.comment.body, 'C1')


class AttachmentMethodsTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.attach = File()
        self.attach.data = 'Data 1'
        self.methods = AttachmentMethods(self.attach, TestRequest())

    def test_getData(self):
        self.assertEqual(base64.decodestring(self.methods.getData()),
                         'Data 1')

    def test_setData(self):
        self.methods.setData(base64.encodestring('Data 1'))
        self.assertEqual(self.attach.data, 'Data 1')
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TrackerMethodsTest),
        unittest.makeSuite(BugMethodsTest),
        unittest.makeSuite(CommentMethodsTest),
        unittest.makeSuite(AttachmentMethodsTest),
        ))

if __name__ == '__main__':
    unittest.main()
        
    
