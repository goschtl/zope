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
$Id: testObjectName.py,v 1.2 2002/06/14 16:50:19 srichter Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Interface import Interface

from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture import getService, getView, getAdapter

from Zope.I18n.IUserPreferredCharsets import IUserPreferredCharsets

from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.Publisher.HTTP.tests.TestRequest import TestRequest
from Zope.Publisher.HTTP.HTTPRequest import IHTTPRequest
from Zope.Publisher.HTTP.HTTPCharsets import HTTPCharsets

from Zope.Proxy.ContextWrapper import ContextWrapper

from Zope.App.ZopePublication.TraversalViews.ObjectName \
    import IObjectName, ObjectName, SiteObjectName


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
                    [ObjectName])
        provideView(IRoot, 'object_name', IBrowserPresentation,
                    [SiteObjectName])
                    
        provideAdapter = getService(None, "Adapters").provideAdapter
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)    
        provideAdapter(None, IObjectName, [ObjectName])
        provideAdapter(IRoot, IObjectName, [ObjectName])

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

    def testAdapterBadObject(self):
        adapter = getAdapter(None, IObjectName)
        self.assertRaises(TypeError, adapter)
        
    def testAdapterNoContext(self):
        adapter = getAdapter(Root(), IObjectName)
        self.assertRaises(TypeError, adapter)
    
    def testAdapterBasicContext(self):
        content = ContextWrapper(TrivialContent(), Root(), name='a')
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        adapter = getAdapter(content, IObjectName)
        self.assertEqual(adapter(), 'c')
        
def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

