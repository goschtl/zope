##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
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

from zwiki.wikipage import WikiPage
from zwiki.interfaces import IWikiPage

class Test(unittest.TestCase):

    def makeTestObject(self):
        return WikiPage()

    def test_Interface(self):
        page = self.makeTestObject()
        self.failUnless(IWikiPage.providedBy(page))

    def test_source(self):
        page = self.makeTestObject()
        self.assertEqual('', page.source)
        page.source = 'foo'
        self.assertEqual('foo', page.source)

    def test_type(self):
        page = self.makeTestObject()
        self.assertEqual('zope.source.rest', page.type)
        page.type = 'foo'
        self.assertEqual('foo', page.type)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))

if __name__ == '__main__':
    unittest.main()
