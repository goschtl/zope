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

$Id: testServices.py,v 1.2 2002/11/30 18:39:17 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Interface import Interface
from Zope.App.OFS.Services.ServiceManager.Browser.Services import Services
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.ComponentArchitecture.GlobalViewService import provideView
from Zope.Publisher.Browser.BrowserView import BrowserView


class SM:

    def __init__(self, **data):
        self._data = data

    def getBoundServiceTypes(self):
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


class V(BrowserView):

    _update = 0

    def setPrefix(self, p):
        self._prefix = p

    def update(self):
        self._update += 1

class Test(PlacelessSetup, TestCase):

    def test_update(self):
        provideView(I, 'ChangeConfigurations', IBrowserPresentation, V)

        r1 = Registry(None)
        r2 = Registry(1)
        r3 = Registry(1)

        sm = SM(test1=r1, test2=r2, test3=r3)

        services = Services(sm, TestRequest()).update()

        self.assertEqual(len(services), 3)

        self.assertEqual(services[0]['name'], 'test1')
        self.assertEqual(services[0]['active'], False)
        self.assertEqual(services[0]['inactive'], True)
        self.assertEqual(services[0]['view'].context, r1)
        self.assertEqual(services[0]['view']._prefix, "test1")
        self.assertEqual(services[0]['view']._update, 1)

        self.assertEqual(services[1]['name'], 'test2')
        self.assertEqual(services[1]['active'], True)
        self.assertEqual(services[1]['inactive'], False)
        self.assertEqual(services[1]['view'].context, r2)
        self.assertEqual(services[1]['view']._prefix, "test2")
        self.assertEqual(services[1]['view']._update, 1)

        self.assertEqual(services[2]['name'], 'test3')
        self.assertEqual(services[2]['active'], True)
        self.assertEqual(services[2]['inactive'], False)
        self.assertEqual(services[2]['view'].context, r3)
        self.assertEqual(services[2]['view']._prefix, "test3")
        self.assertEqual(services[2]['view']._update, 1)
        
        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
