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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: testZDCAnnotatableAdapter.py,v 1.2 2002/10/04 19:05:51 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.tests.PlacelessSetup import PlacelessSetup

class TestAnnotations(dict):

    __implements__ = IAnnotations
    

class Test(PlacelessSetup, TestCase):

    def testZDCAnnotatableAdapter(self):

        from Zope.App.DublinCore.ZDCAnnotatableAdapter \
             import ZDCAnnotatableAdapter

        annotations = TestAnnotations()
        dc = ZDCAnnotatableAdapter(annotations)

        self.failIf(annotations, "There shouldn't be any data yet")
        self.assertEqual(dc.title, u'')
        self.failIf(annotations, "There shouldn't be any data yet")
        dc.title = u"Test title"
        self.failUnless(annotations, "There should be data now!")
        
        dc = ZDCAnnotatableAdapter(annotations)
        self.assertEqual(dc.title, u'Test title')
        
        
    

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
