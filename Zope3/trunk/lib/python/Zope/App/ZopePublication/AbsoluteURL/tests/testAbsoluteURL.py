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
"""Test the AbsoluteURL view

Revision information:
$Id: testAbsoluteURL.py,v 1.2 2002/06/10 23:29:20 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup

from Zope.ComponentArchitecture import getService, getView
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.Publisher.HTTP.tests.TestRequest import TestRequest
from Zope.Proxy.ContextWrapper import ContextWrapper
from Interface import Interface

class IRoot(Interface): pass

class Root:
    __implements__ = IRoot
    
class TrivialContent(object):
    """Trivial content object, used because instances of object are rocks."""

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        from Zope.App.ZopePublication.AbsoluteURL.AbsoluteURL \
             import AbsoluteURL, SiteAbsoluteURL
        provideView=getService(None,"Views").provideView
        provideView(None, 'absolute_url', IBrowserPresentation,
                    [AbsoluteURL])
        provideView(IRoot, 'absolute_url', IBrowserPresentation,
                    [SiteAbsoluteURL])

    def testBadObject(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)
        view = getView(None, 'absolute_url', request)
        self.assertRaises(TypeError, view.__str__)
        
    def testNoContext(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)
        view = getView(Root(), 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com')
        
    def testBasicContext(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        content = ContextWrapper(TrivialContent(), Root(), name='a')
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/a/b/c')

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

