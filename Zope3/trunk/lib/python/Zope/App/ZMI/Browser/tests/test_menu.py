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

$Id: test_menu.py,v 1.1 2002/12/20 23:00:26 jim Exp $
"""

import unittest
from Interface import Interface

from Zope.ComponentArchitecture import getService, getServiceManager
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
           import PlacefulSetup

from Zope.App.ZMI.Browser.menu import MenuAccessView

from Zope.Publisher.Browser.IBrowserView import IBrowserView
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.App.ZopePublication.Traversers import TestTraverser
from Zope.Security.SecurityManagement import newSecurityManager
from Zope.Security.Checker import defineChecker, NamesChecker, CheckerPublic
from Zope.Security.Proxy import ProxyFactory
from Zope.App.Publisher.Browser.IBrowserMenuService \
     import IBrowserMenuService

def d(title, action):
    return {'action': action, 'title': title, 'description': ''}

class Service:
    __implements__ = IBrowserMenuService

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
        getService(None,"Views").provideView(
            I, 'a3', IBrowserPresentation, [V])
        getService(None, "Views").provideView(None, '_traverse',
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

