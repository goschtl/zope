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

$Id: test_comment.py,v 1.1 2003/07/24 18:08:38 srichter Exp $
"""
import unittest

from bugtracker.interfaces import IComment
from bugtracker.comment import Comment

class CommentTest(unittest.TestCase):

    def setUp(self):
        self.comment = Comment()

    def test_Interface(self):
        self.failUnless(IComment.providedBy(self.comment))

    def test_body(self):
        self.assertEqual(self.comment.body, u'')
        self.comment.body = u'test'
        self.assertEqual(self.comment.body, u'test')
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CommentTest),
        ))

if __name__ == '__main__':
    unittest.main()
