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
"""Unit test for AnnotationCacheable adapter.

$Id: testAnnotationCacheable.py,v 1.2 2002/10/03 10:37:50 mgedmin Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture import getService
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.OFS.Annotation.IAttributeAnnotatable import IAttributeAnnotatable
from Zope.App.OFS.Annotation.AttributeAnnotations import AttributeAnnotations
from Zope.App.Caching.AnnotationCacheable import AnnotationCacheable

class ObjectStub:
    __implements__ = IAttributeAnnotatable

class TestAnnotationCacheable(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        getService(None, "Adapters").provideAdapter(
            IAttributeAnnotatable, IAnnotations,
            AttributeAnnotations)

    def testNormal(self):
        ob = ObjectStub()
        adapter = AnnotationCacheable(ob)
        self.assertEquals(adapter.getCacheId(), None,
                          "initially cache ID should be None")

        adapter.setCacheId("my_id")
        self.assertEquals(adapter.getCacheId(), "my_id",
                          "failed to set cache ID")


def test_suite():
    return TestSuite((
        makeSuite(TestAnnotationCacheable),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
