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

$Id: test_componentpathwidget.py,v 1.5 2003/11/27 13:59:14 philikon Exp $
"""
__metaclass__ = type

import unittest
from zope.app.tests import ztapi
from zope.app.browser.services.registration import ComponentPathWidget
from zope.app.interfaces.services.registration import IComponentRegistration
from zope.app.interfaces.traversing import IPhysicallyLocatable
from zope.app.interfaces.traversing import ITraverser, ITraversable
from zope.app.services.field import ComponentPath
from zope.app.location import LocationPhysicallyLocatable
from zope.app.traversing.adapters import Traverser, DefaultTraversable
from zope.app.tests import ztapi
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.interface import implements, Interface
from zope.publisher.browser import TestRequest, BrowserView
from zope.app.container.contained import Contained

class Component:
    implements(Interface)

class SiteManagementFolder:
    foo = Component()

class RegistrationManager:
    pass

class Registration(Contained):
    implements(IComponentRegistration)

    path = 'foo'


class AbsoluteURL(BrowserView):

    def __str__(self):
        return 'something'
    

class ComponentPathWidgetTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(ComponentPathWidgetTest, self).setUp()
        ztapi.provideAdapter(None, ITraverser, Traverser)
        ztapi.provideAdapter(None, ITraversable, DefaultTraversable)
        ztapi.provideAdapter(None, IPhysicallyLocatable,
                             LocationPhysicallyLocatable)
        ztapi.browserView(Interface, "absolute_url", AbsoluteURL)

        field = ComponentPath(None, title=u"Path")
        field.__name__ = u'path'

        folder = SiteManagementFolder()
        rm = RegistrationManager(); rm.__parent__ = folder
        reg = Registration(); reg.__parent__ = rm
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
        comp = Component()
        comp.__name__ = "path2"
        self.widget.context.context = comp
        self.assertEqual(self.widget.getInputValue(), 'path2')

    def test_call(self):
        self.assertEqual(
            self.widget(),
            '<a href="something/@@SelectedManagementView.html">foo</a>')
        comp = Component()
        comp.__name__ = "path2"
        self.widget.context.context = comp
        self.assertEqual(
            self.widget(),
            '<a href="something/@@SelectedManagementView.html">path2</a>')

    

def test_suite():
    return unittest.makeSuite(ComponentPathWidgetTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
