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
"""ComponentPathWidget tests.

$Id: test_componentpathwidget.py,v 1.1 2003/08/16 19:17:11 srichter Exp $
"""
__metaclass__ = type

import unittest
from zope.app.browser.services.registration import ComponentPathWidget
from zope.app.context import ContextWrapper
from zope.app.interfaces.services.registration import IComponentRegistration
from zope.app.interfaces.traversing import \
     IContainmentRoot, ITraverser, ITraversable, IPhysicallyLocatable
from zope.app.services.field import ComponentPath
from zope.app.traversing.adapters import \
     Traverser, DefaultTraversable, WrapperPhysicallyLocatable
from zope.component.adapter import provideAdapter
from zope.component.view import provideView
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.interface import implements, Interface
from zope.publisher.browser import TestRequest, BrowserView
from zope.publisher.interfaces.browser import IBrowserPresentation

class Component:
    implements(Interface)

class Registration:
    implements(IComponentRegistration)

    path = 'foo'

    foo = Component()

class AbsoluteURL(BrowserView):

    def __str__(self):
        return 'something'
    

class ComponentPathWidgetTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(None, ITraverser, Traverser)
        provideAdapter(None, ITraversable, DefaultTraversable)
        provideAdapter(None, IPhysicallyLocatable, WrapperPhysicallyLocatable)
        provideView(Interface, "absolute_url", IBrowserPresentation,
                    AbsoluteURL)

        field = ComponentPath(None, title=u"Path")
        field.__name__ = u'path'
        reg = ContextWrapper(Registration(), None, name="reg")
        field = field.bind(reg)
        self.widget = ComponentPathWidget(field, TestRequest())

    def test_hidden(self):
        self.assertEqual(self.widget.hidden(), '')

    def test_hasInput(self):
        self.assertEqual(self.widget.hasInput(), True)
        self.widget.request.form['field.path'] = 'foo'
        self.assertEqual(self.widget.hasInput(), True)

    def test_getInputValue(self):
        self.assertEqual(self.widget.getInputValue(), 'foo')
        comp = ContextWrapper(Component(), None, name="path2")
        self.widget.context.context = comp
        self.assertEqual(self.widget.getInputValue(), 'path2')

    def test_call(self):
        self.assertEqual(
            self.widget(),
            '<a href="something/@@SelectedManagementView.html">foo</a>')
        comp = ContextWrapper(Component(), None, name="path2")
        self.widget.context.context = comp
        self.assertEqual(
            self.widget(),
            '<a href="something/@@SelectedManagementView.html">path2</a>')

    

def test_suite():
    return unittest.makeSuite(ComponentPathWidgetTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
