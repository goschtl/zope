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

$Id: test_wikipage.py,v 1.1 2003/12/16 10:05:56 nmurthy Exp $
"""
import unittest

from zope.products.zwiki.wikipage import WikiPage
from zope.products.zwiki.interfaces import IWikiPage


class Test(unittest.TestCase):

    def makeTestObject(self):
        return WikiPage()

    def test_Interface(self):
        page = self.makeTestObject()
        self.failUnless(IWikiPage.isImplementedBy(page))

    def test_source(self):
        page = self.makeTestObject()
        self.assertEqual('', page.source)
        page.source = 'foo'
        self.assertEqual('foo', page.source)

    def test_type(self):
        page = self.makeTestObject()
        self.assertEqual('reStructured Text (reST)', page.type)
        page.type = 'foo'
        self.assertEqual('foo', page.type)

    def test_append(self):
        page = self.makeTestObject()
        page.source = 'the source'
        page.append(', more source')
        self.assertEqual('the source, more source', page.source)

    def test_comment(self):
        page = self.makeTestObject()
        page.source = 'the source'
        self.assertEqual(1, page.__dict__['_WikiPage__comments'])
        page.comment('\n\nthis is a comment')
        self.assertEqual("the source\n\nthis is a comment", page.source)
        self.assertEqual(2, page.__dict__['_WikiPage__comments'])

    def test_getCommentCounter(self):
        page = self.makeTestObject()
        self.assertEqual(1, page.getCommentCounter())
        page.comment('comment')
        self.assertEqual(2, page.getCommentCounter())
        
        
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))

if __name__ == '__main__':
    unittest.main()
