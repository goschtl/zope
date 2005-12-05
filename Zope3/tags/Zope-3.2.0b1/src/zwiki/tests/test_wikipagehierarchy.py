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

from zope.interface import implements, classImplements
from zope.app.testing import ztapi

from zope.app.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.location.interfaces import ILocation

from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.location.traversing import LocationPhysicallyLocatable

from zwiki.interfaces import IWikiPage, IWikiPageHierarchy
from zwiki.wikipage import WikiPage, WikiPageHierarchyAdapter
from zwiki.wiki import Wiki

class TestAnnotations(dict):
    implements(IAnnotations)


class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        # This needs to be done, since the IAttributeAnnotable interface
        # is usually set in the ZCML
        classImplements(WikiPage, IAttributeAnnotatable);
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                       AttributeAnnotations)
        ztapi.provideAdapter(IWikiPage, IWikiPageHierarchy,
                       WikiPageHierarchyAdapter)
        ztapi.provideAdapter(ILocation, IPhysicallyLocatable, LocationPhysicallyLocatable)
        self.page = WikiPage()

    def makeTestObject(self):
        return WikiPageHierarchyAdapter(self.page)

    def test_Interface(self):
        hier = self.makeTestObject()
        self.failUnless(IWikiPageHierarchy.providedBy(hier))

    def test_parents(self):
        hier = self.makeTestObject()
        self.assertEqual((), hier.parents)
        hier.parents = ('foo',)
        self.assertEqual(('foo',), hier.parents)
        # Test whether the annotations stay.
        hier = self.makeTestObject()
        self.assertEqual(('foo',), hier.parents)

    def test_reparent(self):
        hier = self.makeTestObject()
        hier.parents = ('foo',)
        self.assertEqual(('foo',), hier.parents)
        hier.reparent(('bar',))
        self.assertEqual(('bar',), hier.parents)

    def test_wikipath(self):
        wiki = Wiki()
        wiki['TopLevelPage'] = WikiPage()
        wiki['SecondLevelPage'] = WikiPage()
        hier = WikiPageHierarchyAdapter(wiki['SecondLevelPage'])
        hier.reparent(('TopLevelPage',))
        self.assertEqual([wiki['TopLevelPage'], wiki['SecondLevelPage']],
                         hier.path())

    def test_findChildren(self):
        wiki = Wiki()

        page1 = WikiPage()
        wiki['TopLevelPage'] = page1
        # get the item again so it'll be wrapped in ContainedProxy
        page1 = wiki['TopLevelPage']
        hier1 = WikiPageHierarchyAdapter(page1)

        page2 = WikiPage()
        wiki['SecondLevelPage'] = page2
        # get the item again so it'll be wrapped in ContainedProxy
        page2 = wiki['SecondLevelPage']
        hier2 = WikiPageHierarchyAdapter(page2)
        hier2.reparent(('TopLevelPage',))

        page3 = WikiPage()
        wiki['ThirdLevelPage'] = page3
        # get the item again so it'll be wrapped in ContainedProxy
        page3 = wiki['ThirdLevelPage']
        hier3 = WikiPageHierarchyAdapter(page3)
        hier3.reparent(('SecondLevelPage',))

        self.assertEqual(( (page2, ()), ),
                         hier1.findChildren(False));

        self.assertEqual(((page2, ((page3, ()),) ),),
                         hier1.findChildren());
        
    
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))

if __name__ == '__main__':
    unittest.main()
