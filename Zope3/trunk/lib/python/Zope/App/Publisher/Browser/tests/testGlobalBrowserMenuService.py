##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

$Id: testGlobalBrowserMenuService.py,v 1.1 2002/06/18 19:34:57 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Publisher.Browser.IBrowserPublisher import IBrowserPublisher
from Zope.Exceptions import Forbidden, Unauthorized, DuplicationError
from Interface import Interface
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup

class I1(Interface): pass
class I11(I1): pass
class I12(I1): pass
class I111(I11): pass

class X:
    __implements__ = IBrowserPublisher, I111

    def f(self): pass

    def browserDefault(self, r): return self, ()
    def publishTraverse(self, request, name):
        if name[:1] == 'f':
            raise Forbidden, name
        if name[:1] == 'u':
            raise Unauthorized, name
        return self.f


class Test(PlacelessSetup, TestCase):

    def __reg(self):
        from Zope.App.Publisher.Browser.GlobalBrowserMenuService \
             import GlobalBrowserMenuService
        
        r = GlobalBrowserMenuService()
        return r
    
    def testDup(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')
        self.assertRaises(DuplicationError, r.menu, 'test_id', 'test menu')
        
    def test(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')
        r.menuItem('test_id', Interface, 'a1', 't1', 'd1')
        r.menuItem('test_id', I1, 'a2', 't2', 'd2')
        r.menuItem('test_id', I11, 'a3', 't3', 'd3', 'context')
        r.menuItem('test_id', I11, 'a4', 't4', 'd4', 'not:context')
        r.menuItem('test_id', I111, 'a5', 't5', 'd5')
        r.menuItem('test_id', I111, 'a6', 't6', 'd6')
        r.menuItem('test_id', I111, 'f7', 't7', 'd7')
        r.menuItem('test_id', I111, 'u8', 't8', 'd8')
        r.menuItem('test_id', I12, 'a9', 't9', 'd9')

        menu = r.getMenu('test_id', X(), TestRequest())

        def d(n):
            return {'action': "a%s" % n,
                    'title':  "t%s" % n,
                    'description':  "d%s" % n,
                    }
        
        self.assertEqual(list(menu), [d(5), d(6), d(3), d(2), d(1)])
        
    def testEmpty(self):
        r = self.__reg()
        r.menu('test_id', 'test menu')
        menu = r.getMenu('test_id', X(), TestRequest())        
        self.assertEqual(list(menu), [])


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
