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
"""Unit test for the generic NameComponentRegistry view mixin

$Id: test_namecomponentregistryview.py,v 1.2 2003/11/21 17:11:57 jim Exp $
"""

from zope.app.tests import ztapi
from unittest import TestCase, TestSuite, main, makeSuite
from zope.interface import Interface, implements
from zope.publisher.browser import TestRequest
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.tests import ztapi
from zope.publisher.browser import BrowserView
from zope.app.browser.services.registration import NameComponentRegistryView
from zope.app.interfaces.traversing import ITraversable, ITraverser
from zope.app.traversing.adapters import Traverser


class SM:

    def __init__(self, **data):
        self._data = data

    def listRegistrationNames(self):
        return self._data.keys()

    def queryRegistrations(self, name):
        return self._data[name]

class I(Interface): pass

class Registry:
    implements(I)

    def __init__(self, active):
        self._active = active

    def active(self):
        return self._active

class ITestRegistration(Interface): pass

class Registration:

    implements(ITestRegistration, ITraversable)

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
        ztapi.provideAdapter(None, ITraverser, Traverser)
        ztapi.browserView(I, 'ChangeRegistrations', V)
        ztapi.browserView(ITestRegistration, 'absolute_url', AU)

        r1 = Registry(None)
        r2 = Registry(Registration('1'))
        r3 = Registry(Registration('1'))

        sm = SM(test1=r1, test2=r2, test3=r3)

        services = NameComponentRegistryView(sm, TestRequest()).update()

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
