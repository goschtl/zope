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

Revision information:
$Id: testResources.py,v 1.1 2002/06/13 23:15:44 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalResourceService import provideResource
from Zope.Publisher.Browser.IBrowserView import IBrowserView

class Test(PlacelessSetup, TestCase):

    def test(self):
        from Zope.App.Publisher.Browser.Resources import Resources
        request = TestRequest()

        class Resource:
            def __init__(self, request): pass
            def __call__(self): return 42

        provideResource('test', IBrowserView, Resource)
        view = Resources(None, request)
        resource = view.publishTraverse(request, 'test')
        self.assertEqual(resource(), 42)
        
        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
