##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Adding implementation tests

$Id: testAdding.py,v 1.2 2002/07/17 16:54:17 jeremy Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Zope.App.OFS.Container.Views.Browser.Adding import Adding
from Zope.App.OFS.Container.IAdding import IAdding
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.ComponentArchitecture.GlobalViewService import provideView

class Container:
    data = ()
    def setObject(self, *args):
        self.data += args

class CreationView(BrowserView):

    def action(self):
        return 'been there, done that'

class Test(PlacelessSetup, TestCase):

    def test(self):
        container = Container()
        request = TestRequest()
        adding = Adding(container, request)
        provideView(IAdding, "Thing", IBrowserPresentation, CreationView)
        
        self.assertEqual(adding.contentName, None)
        view = adding.publishTraverse(request, 'Thing=foo') 
        self.assertEqual(view.action(), 'been there, done that')
        self.assertEqual(adding.contentName, 'foo')
        adding.add(42)
        self.assertEqual(container.data, ('foo', 42))

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')



