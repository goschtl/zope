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
$Id: testResources.py,v 1.3 2002/06/14 16:50:19 srichter Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalResourceService import provideResource
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter

from Zope.I18n.IUserPreferredCharsets import IUserPreferredCharsets

from Zope.Publisher.HTTP.HTTPRequest import IHTTPRequest
from Zope.Publisher.HTTP.HTTPCharsets import HTTPCharsets
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.Publisher.Browser.IBrowserView import IBrowserView

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)    


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
        
    def testNotFound(self):
        from Zope.App.Publisher.Browser.Resources import Resources
        from Zope.Exceptions import NotFoundError
        request = TestRequest()
        view = Resources(None, request)
        self.assertRaises(NotFoundError, 
                          view.publishTraverse, 
                          request, 'test'
                          )
    
        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
