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
import unittest

from zope.component import getService
from zope.app.services.servicenames import Views
from zope.interface import Interface

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.services.tests.placefulsetup import PlacefulSetup


class I1(Interface):
    pass

class C1:
    __implements__ = I1

class InstanceWithContext:
    def __init__(self, context):
        self.context = context

class InstanceWithoutContext:
    pass

class TestViewZPT(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.t = ViewPageTemplateFile('test.pt')
        self.context = C1()


    def checkNamespaceContextAvailable(self):
        context = self.context
        request = None

        namespace = self.t.pt_getContext(InstanceWithContext(context), request)
        self.failUnless(namespace['context'] is context)
        self.failUnless('views' in namespace)


    def checkNamespaceHereNotAvailable(self):
        request = None
        self.assertRaises(AttributeError, self.t.pt_getContext,
                          InstanceWithoutContext(), request)

    def checkViewMapper(self):

        the_view = "This is the view"
        class the_view_type(Interface): pass
        the_view_name = "some view name"
        def ViewMaker(*args, **kw):
            return the_view

        getService(None,Views).provideView(I1,
                    name=the_view_name,
                    type=the_view_type,
                    maker=[ViewMaker])

        from zope.component.interfaces \
             import IPresentationRequest

        class MyRequest:
            __implements__ = IPresentationRequest
            def getPresentationType(self):
                return the_view_type
            def getPresentationSkin(self):
                return "some skin"

        request = MyRequest()

        namespace = self.t.pt_getContext(InstanceWithContext(self.context),
                                         request)
        views = namespace['views']
        self.failUnless(the_view is views[the_view_name])


class TestViewZPTUsage(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.context = C1()
        self.context.request = None

    def checkInitWithUsage(self):
        self.t = ViewPageTemplateFile('testusage.pt', usage="test")
        result = self.t(self.context)
        self.assertEquals(result, "<html><body>test</body></html>")
        result = self.t(self.context, template_usage="other")
        self.assertEquals(result, "<html><body>other</body></html>")

    def checkInitWithoutUsage(self):
        self.t = ViewPageTemplateFile('testusage.pt')
        result = self.t(self.context)
        self.assertEquals(result, "<html><body></body></html>")
        result = self.t(self.context, template_usage="other")
        self.assertEquals(result, "<html><body>other</body></html>")


def test_suite():
    return unittest.makeSuite(TestViewZPT, 'check')
    return unittest.makeSuite(TestViewZPTUsage, 'check')

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
