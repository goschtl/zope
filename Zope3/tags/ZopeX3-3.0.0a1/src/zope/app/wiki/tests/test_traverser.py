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
from zope.component.tests.request import Request
from zope.component import getService
from zope.app.servicenames import Presentation
from zope.interface import Interface
from zope.exceptions import NotFoundError
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.proxy import removeAllProxies

from zope.app.wiki.interfaces import IWikiPage
from zope.app.wiki.wiki import Wiki
from zope.app.wiki.wikipage import WikiPage
from zope.app.wiki.traversal import WikiPageTraverser

class I(Interface):
    pass

class Request(Request):
    def getEffectiveURL(self):
        return ''

class View:
    def __init__(self, comp, request):
        self._comp = comp

class TestTraverser(PlacelessSetup, unittest.TestCase):

    def testAttr(self):
        wiki = Wiki()
        page1 = WikiPage()
        page2 = WikiPage()
        wiki['FrontPage'] = page1
        wiki['FooBar'] = page2
        # get the items again so they'll be wrapped in ContainedProxy
        page1 = wiki['FrontPage']
        page2 = wiki['FooBar']
        request = Request(I, '')

        T = WikiPageTraverser(page1, request)
        self.failUnless(
            removeAllProxies(T.publishTraverse(request, 'FooBar')) is page2)

        self.assertRaises(NotFoundError, T.publishTraverse, request,'morebar')

    def testView(self):
        wiki = Wiki()
        page1 = WikiPage()
        page2 = WikiPage()
        wiki['FrontPage'] = page1
        wiki['FooBar'] = page2
        # get the items again so they'll be wrapped in ContainedProxy
        page1 = wiki['FrontPage']
        page2 = wiki['FooBar']
        request = Request(I, '')

        T = WikiPageTraverser(page1, request)
        getService(None, Presentation).provideView(
            IWikiPage, 'viewfoo', I, View)

        self.failUnless(
            T.publishTraverse(request, 'viewfoo').__class__ is View )
        self.failUnless(
            removeAllProxies(T.publishTraverse(request, 'FooBar')) is page2)

        self.assertRaises(NotFoundError, T.publishTraverse, request, 'morebar')
        self.assertRaises(NotFoundError, T.publishTraverse, request,
                          '@@morebar')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestTraverser),
        ))

if __name__ == '__main__':
    unittest.main()
