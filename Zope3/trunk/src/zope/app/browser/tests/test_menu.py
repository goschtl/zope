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
"""

$Id: test_menu.py,v 1.7 2003/03/03 23:16:06 gvanrossum Exp $
"""

import unittest
from zope.interface import Interface

from zope.component import getService, getServiceManager
from zope.app.services.servicenames import Views
from zope.app.services.tests.placefulsetup \
           import PlacefulSetup

from zope.app.browser.menu import MenuAccessView

from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.publication.traversers import TestTraverser
from zope.security.management import newSecurityManager
from zope.security.checker import defineChecker, NamesChecker, CheckerPublic
from zope.security.proxy import ProxyFactory
from zope.app.interfaces.publisher.browser import IBrowserMenuService
from zope.app.interfaces.services.interfaces import ISimpleService

def d(title, action):
    return {'action': action, 'title': title, 'description': ''}

class Service:
    __implements__ = IBrowserMenuService, ISimpleService

    def getMenu(self, name, ob, req):
        return [d('l1', 'a1'),
                d('l2', 'a2/a3'),
                d('l3', '@@a3'),]

class I(Interface): pass
class C:
    __implements__ = I

    def __call__(self):
        pass

ob = C()
ob.a1 = C()
ob.a2 = C()
ob.a2.a3 = C()
ob.abad = C()
ob.abad.bad = 1

class V:
    __implements__ = IBrowserView

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        pass


class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        defineService = getServiceManager(None).defineService
        provideService = getServiceManager(None).provideService


        defineService('BrowserMenu', IBrowserMenuService)
        provideService('BrowserMenu', Service())
        getService(None,Views).provideView(
            I, 'a3', IBrowserPresentation, [V])
        getService(None, Views).provideView(None, '_traverse',
                            IBrowserPresentation, [TestTraverser])
        defineChecker(C, NamesChecker(['a1', 'a2', 'a3', '__call__'],
                                      CheckerPublic,
                                      abad='waaa'))

    def test(self):
        newSecurityManager('who')
        v = MenuAccessView(ProxyFactory(ob), Request())
        self.assertEqual(v['zmi_views'],
                         [{'description': '', 'title':'l1', 'action':'a1'},
                          {'description': '', 'title':'l2', 'action':'a2/a3'},
                          {'description': '', 'title':'l3', 'action':'@@a3'}
                          ])


class Request:
    def getPresentationType(self):
        return IBrowserPresentation
    def getPresentationSkin(self):
        return ''

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
