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
"""Browser Menu Browser Tests

$Id: tests.py,v 1.1 2004/03/10 23:10:44 srichter Exp $
"""
import unittest

from zope.app.tests import ztapi
from zope.interface import Interface, implements

from zope.component import getServiceManager
from zope.app.services.tests.placefulsetup import PlacefulSetup

from zope.app.menu.browser import MenuAccessView
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserView
from zope.app.publisher.interfaces.browser import IBrowserMenuService
from zope.app.publication.traversers import TestTraverser
from zope.security.management import newSecurityManager
from zope.security.checker import defineChecker, NamesChecker, CheckerPublic
from zope.security.proxy import ProxyFactory
from zope.app.interfaces.services.service import ISimpleService

def d(title, action):
    return {'action': action, 'title': title, 'description': ''}

class Service:
    implements(IBrowserMenuService, ISimpleService)

    def getMenu(self, name, ob, req):
        return [d('l1', 'a1'),
                d('l2', 'a2/a3'),
                d('l3', '@@a3'),]

class I(Interface): pass
class C:
    implements(I)

    def __call__(self):
        pass

ob = C()
ob.a1 = C()
ob.a2 = C()
ob.a2.a3 = C()
ob.abad = C()
ob.abad.bad = 1

class V:
    implements(IBrowserView)

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
        ztapi.browserView(I, 'a3', [V])
        ztapi.browserView(None, '_traverse', [TestTraverser])
        defineChecker(C, NamesChecker(['a1', 'a2', 'a3', '__call__'],
                                      CheckerPublic,
                                      abad='waaa'))

    def test(self):
        newSecurityManager('who')
        v = MenuAccessView(ProxyFactory(ob), TestRequest())
        self.assertEqual(v['zmi_views'],
                         [{'description': '', 'title':'l1', 'action':'a1'},
                          {'description': '', 'title':'l2', 'action':'a2/a3'},
                          {'description': '', 'title':'l3', 'action':'@@a3'}
                          ])


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
