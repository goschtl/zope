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
$Id: testObjectName.py,v 1.5 2002/10/04 18:37:24 jim Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Interface import Interface

from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture import getService, getView, getAdapter

from Zope.I18n.IUserPreferredCharsets import IUserPreferredCharsets

from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.Publisher.HTTP.tests.TestRequest import TestRequest
from Zope.Publisher.HTTP.HTTPRequest import IHTTPRequest
from Zope.Publisher.HTTP.HTTPCharsets import HTTPCharsets

from Zope.Proxy.ContextWrapper import ContextWrapper

from Zope.App.ZopePublication.TraversalViews.ObjectName \
    import ObjectNameView, SiteObjectNameView

class IRoot(Interface): pass

class Root:
    __implements__ = IRoot
    
class TrivialContent(object):
    """Trivial content object, used because instances of object are rocks."""

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideView = getService(None, "Views").provideView
        provideView(None, 'object_name', IBrowserPresentation,
                    [ObjectNameView])
        provideView(IRoot, 'object_name', IBrowserPresentation,
                    [SiteObjectNameView])
                    
        provideAdapter = getService(None, "Adapters").provideAdapter
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)    

    def testViewBadObject(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)
        view = getView(None, 'object_name', request)
        self.assertRaises(TypeError, view.__str__)
        
    def testViewNoContext(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)
        view = getView(Root(), 'object_name', request)
        self.assertRaises(TypeError, str(view))
        
    def testViewBasicContext(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        content = ContextWrapper(TrivialContent(), Root(), name='a')
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        view = getView(content, 'object_name', request)
        self.assertEqual(str(view), 'c')
        
def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')

