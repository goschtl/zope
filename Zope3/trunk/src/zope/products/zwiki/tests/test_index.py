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

$Id: test_index.py,v 1.1 2003/12/16 10:05:56 nmurthy Exp $
"""
import unittest
from zope.interface import implements
from zope.app.index.text.tests import test_index
from zope.app.interfaces.index.text import ISearchableText
from zope.app.interfaces.container import IContained
from zope.app.services.tests.placefulsetup import PlacefulSetup

from zope.products.zwiki.interfaces import IWikiPage
from zope.products.zwiki.index import WikiTextIndex


class FakeSearchableObject:
    implements(ISearchableText, IWikiPage, IContained)

    __parent__ = None
    __name__ = None

    def __init__(self):
        self.texts = [u"Bruce"]

    def getSearchableText(self):
        return self.texts


class IndexTest(test_index.Test):

    # Note: There could be some more testing, checking that only WikiPage
    #       objects get indexed, but we can do this later. Good enoug for
    #       now.

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.index = WikiTextIndex()
        self.rootFolder['myIndex'] = self.index
        self.object = FakeSearchableObject()
        self.rootFolder['bruce'] = self.object


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(IndexTest),
        ))

if __name__ == '__main__':
    unittest.main()
