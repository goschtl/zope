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
"""ZWiki Tests

$Id$
"""
import unittest

from zope.app.wiki.wikipage import Comment
from zope.app.wiki.interfaces import IComment

class TestComment(unittest.TestCase):

    def setUp(self):
        self.comment = Comment()

    def test_Interface(self):
        self.failUnless(IComment.providedBy(self.comment))

    def test_source(self):
        self.assertEqual('', self.comment.source)
        self.comment.source = 'foo'
        self.assertEqual('foo', self.comment.source)

    def test_type(self):
        self.assertEqual('zope.source.rest', self.comment.type)
        self.comment.type = 'foo'
        self.assertEqual('foo', self.comment.type)


    # XXX: Test title


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestComment),
        ))

if __name__ == '__main__':
    unittest.main()
