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
"""Unit test for the generic NameComponentConfigurable view mixin

$Id: test_namecomponentconfigurableview.py,v 1.1 2003/03/21 21:09:34 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.component.view import provideView
from zope.publisher.browser import BrowserView
from zope.app.browser.services.configuration \
     import NameComponentConfigurableView
from zope.app.interfaces.traversing import ITraversable


class SM:

    def __init__(self, **data):
        self._data = data

    def listConfigurationNames(self):
        return self._data.keys()

    def queryConfigurations(self, name):
        return self._data[name]

class I(Interface): pass

class Registry:
    __implements__ = I

    def __init__(self, active):
        self._active = active

    def active(self):
        return self._active

class ITestConfiguration(Interface): pass

class Configuration:

    __implements__ = ITestConfiguration, ITraversable

    def __init__(self, path):
        self.componentPath = path

    def traverse(self, name, parameters, original_name, furtherPath):
        return self

class V(BrowserView):

    _update = 0

    def setPrefix(self, p):
        self._prefix = p

    def update(self):
        self._update += 1

class AU(BrowserView):

    def __str__(self):
        return "/" + self.context.componentPath

class Test(PlacelessSetup, TestCase):

    def test_update(self):
        provideView(I, 'ChangeConfigurations', IBrowserPresentation, V)
        provideView(ITestConfiguration, 'absolute_url', IBrowserPresentation,
                    AU)

        r1 = Registry(None)
        r2 = Registry(Configuration('1'))
        r3 = Registry(Configuration('1'))

        sm = SM(test1=r1, test2=r2, test3=r3)

        services = NameComponentConfigurableView(sm, TestRequest()).update()

        self.assertEqual(len(services), 3)

        self.assertEqual(services[0]['name'], 'test1')
        self.assertEqual(services[0]['active'], False)
        self.assertEqual(services[0]['inactive'], True)
        self.assertEqual(services[0]['view'].context, r1)
        self.assertEqual(services[0]['view']._prefix, "test1")
        self.assertEqual(services[0]['view']._update, 1)
        self.assertEqual(services[0]['url'], None)

        self.assertEqual(services[1]['name'], 'test2')
        self.assertEqual(services[1]['active'], True)
        self.assertEqual(services[1]['inactive'], False)
        self.assertEqual(services[1]['view'].context, r2)
        self.assertEqual(services[1]['view']._prefix, "test2")
        self.assertEqual(services[1]['view']._update, 1)
        self.assertEqual(services[1]['url'], '/1')

        self.assertEqual(services[2]['name'], 'test3')
        self.assertEqual(services[2]['active'], True)
        self.assertEqual(services[2]['inactive'], False)
        self.assertEqual(services[2]['view'].context, r3)
        self.assertEqual(services[2]['view']._prefix, "test3")
        self.assertEqual(services[2]['view']._update, 1)
        self.assertEqual(services[2]['url'], '/1')



def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
