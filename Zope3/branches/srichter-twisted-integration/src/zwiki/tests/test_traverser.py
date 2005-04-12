##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Test wiki page traverser

$Id$
"""
import unittest, sys

from zope.component.tests.request import Request
from zope.interface import Interface, classImplements
from zope.publisher.interfaces import NotFound
from zope.proxy import removeAllProxies

from zope.app import zapi
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.app.location.interfaces import ILocation
from zope.app.location.traversing import LocationPhysicallyLocatable
from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.app.traversing.interfaces import IPhysicallyLocatable

from zwiki.interfaces import IWikiPage, IWikiPageHierarchy
from zwiki.wiki import Wiki
from zwiki.wikipage import WikiPage, WikiPageHierarchyAdapter
from zwiki.traversal import WikiPageTraverser

class I(Interface):
    pass

class Request(Request):
    def getEffectiveURL(self):
        return ''

class View:
    def __init__(self, comp, request):
        self._comp = comp

class TestTraverser(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestTraverser, self).setUp()
        classImplements(WikiPage, IAttributeAnnotatable)
        ztapi.provideAdapter(IWikiPage, IWikiPageHierarchy,
                             WikiPageHierarchyAdapter)
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                             AttributeAnnotations)
        ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                             LocationPhysicallyLocatable)

    def testAttr(self):
        wiki = Wiki()
        page1 = WikiPage()
        wiki['FrontPage'] = page1
        page2 = WikiPage()
        wiki['FooBar'] = page2
        IWikiPageHierarchy(page2).parents = ('FrontPage',)
        request = Request(I)

        T = WikiPageTraverser(page1, request)
        self.failUnless(
            removeAllProxies(T.publishTraverse(request, 'FooBar')) is page2)

        self.assertRaises(NotFound, T.publishTraverse, request,'morebar')

    def testView(self):
        wiki = Wiki()
        page1 = WikiPage()
        wiki['FrontPage'] = page1
        page2 = WikiPage()
        wiki['FooBar'] = page2
        IWikiPageHierarchy(page2).parents = ('FrontPage',)
        request = Request(I)

        T = WikiPageTraverser(page1, request)
        ztapi.provideView(IWikiPage, I, Interface, 'viewfoo', View)

        self.failUnless(
            T.publishTraverse(request, 'viewfoo').__class__ is View )
        self.failUnless(
            removeAllProxies(T.publishTraverse(request, 'FooBar')) is page2)

        self.assertRaises(NotFound, T.publishTraverse, request, 'morebar')
        self.assertRaises(NotFound, T.publishTraverse, request,
                          '@@morebar')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestTraverser),
        ))

if __name__ == '__main__':
    unittest.main()
