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

$Id: test_wikipagefile.py,v 1.1 2004/02/27 11:07:01 philikon Exp $
"""
import unittest

from zope.app.wiki.wikipage import WikiPage
from zope.app.wiki.wikipage import WikiPageReadFile, WikiPageWriteFile

class ReadFileTest(unittest.TestCase):

    def setUp(self):
        self._page = WikiPage()
        self._page.source = u'This is the source'
        self._file = WikiPageReadFile(self._page)

    def test_read(self): 
        self.assertEqual(self._page.source, self._file.read())

    def test_size(self): 
        self.assertEqual(len(self._page.source), self._file.size())

class WriteFileTest(unittest.TestCase):

    def setUp(self):
        self._page = WikiPage()
        self._file = WikiPageWriteFile(self._page)

    def test_read(self): 
        self._file.write(u'This is the source')
        self.assertEqual(u'This is the source', self._page.source)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ReadFileTest),
        unittest.makeSuite(WriteFileTest),
        ))

if __name__ == '__main__':
    unittest.main()
