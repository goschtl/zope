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
"""

$Id$
"""
import unittest, sys
from zope.exceptions import NotFoundError
from zope.testing.cleanup import CleanUp

from zope.app.wiki.wiki import Wiki
from zope.app.wiki.wikipage import WikiPage
from zope.app.wiki.traversal import WikiPageTraversable

from zope.app.site.tests.placefulsetup import PlacefulSetup

class TestTraversable(PlacefulSetup, CleanUp, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)

    def testAttr(self):
        # test container path traversal
        wiki = Wiki()
        page1 = WikiPage()
        page2 = WikiPage()
        wiki['FrontPage'] = page1
        wiki['FooBar'] = page2
        # get the items again so they'll be wrapped in ContainedProxy
        page1 = wiki['FrontPage']
        page2 = wiki['FooBar']

        T = WikiPageTraversable(page1)
        self.failUnless(T.traverse('FooBar', []) is page2)

        self.assertRaises(NotFoundError , T.traverse, 'morebar', [])


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestTraversable),
        ))

if __name__ == '__main__':
    unittest.main()
