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

$Id: test_wikipagesearchtext.py,v 1.1 2004/02/27 11:07:01 philikon Exp $
"""
import unittest

from zope.app.wiki.wikipage import WikiPage
from zope.app.wiki.wikipage import SearchableText

class SearchableTextTest(unittest.TestCase):

    def setUp(self):
        self._page = WikiPage()
        self._page.source = u'This is the source'
        self._text = SearchableText(self._page)

    def test_getSearchableText(self): 
        self.assertEqual([self._page.source], self._text.getSearchableText())


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SearchableTextTest),
        ))

if __name__ == '__main__':
    unittest.main()
