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

$Id: testFormView.py,v 1.4 2002/07/14 17:31:17 faassen Exp $
"""


from Interface import Interface
from Zope.ComponentArchitecture import getService
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.Publisher.Browser.IBrowserView import IBrowserView
from Zope.Publisher.HTTP.tests.TestRequest import TestRequest

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.Forms.Views.Browser.FormView import FormView

from Zope.App.Forms.Views.Browser.TextWidget import TextWidget
from Zope.App.Forms.Views.Browser.CheckboxWidget import CheckboxWidget

import Schema
from Schema.IField import IStr, IBool
from Schema import _Schema # XXX to wire things up, should fix this

#############################################################################
# If your tests change any global registries, then uncomment the
# following import and include CleanUp as a base class of your
# test. It provides a setUp and tearDown that clear global data that
# has registered with the test cleanup framework.  Don't use this
# tests outside the Zope package.

from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

#############################################################################

class ITestSchema(Interface):
    foo = Schema.Str(title="Foo")
    bar = Schema.Bool(title="Bar")
    
class TestBrowserRequest(TestRequest):
    """Since we have IBrowserViews, we need a request that works
    for IBrowserView.
    """
    def getPresentationType(self):
        return IBrowserView
    
class TestFormView(TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)
        viewService = self.getViewService()
        viewService.provideView(IStr, 'normal', IBrowserView,
                                [TextWidget])
        viewService.provideView(IBool, 'normal', IBrowserView,
                                [CheckboxWidget])
        
    def getViewService(self):
        return getService(None, 'Views')
    
    def test_getWidgetsForSchema(self):
        viewService = self.getViewService()
        view = FormView(None,TestBrowserRequest())
        widgets = view.getWidgetsForSchema(ITestSchema, 'normal')
        # XXX order is undefined. Fix this when we have order.
        self.assert_(isinstance(widgets[0], TextWidget) or
            isinstance(widgets[1], TextWidget))
        self.assert_(isinstance(widgets[0], CheckboxWidget) or
            isinstance(widgets[1], CheckboxWidget))

def test_suite():
    return TestSuite((
        makeSuite(TestFormView),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
