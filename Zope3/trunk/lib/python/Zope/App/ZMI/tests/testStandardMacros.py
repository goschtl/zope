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

$Id: testStandardMacros.py,v 1.2 2002/10/28 11:21:14 stevea Exp $
"""

import unittest, sys
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup\
           import PlacefulSetup
from Zope.ComponentArchitecture import getService
from Zope.Publisher.Browser.IBrowserView import IBrowserView
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Interface import Interface
from Zope.App.ZMI.StandardMacros import Macros 


class ViewWithMacros:
    __implements__ = IBrowserView

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def __call__(self):
        pass

    def __getitem__(self, key):
        return self.pages[key]

    pages = {}

class I(Interface): pass

class C:
    __implements__ = I

class Request:
    def getPresentationType(self):
        return IBrowserPresentation
    def getPresentationSkin(self):
        return ''

class page1(ViewWithMacros):
    pages = {'foo':'page1_foo',
             'bar':'page1_bar'}

class collides_with_page1(ViewWithMacros):
    pages = {'foo':'collides_with_page1_foo',
             'baz':'collides_with_page1_baz'}

class works_with_page1(ViewWithMacros):
    pages = {'fish':'works_with_page1_fish',
             'tree':'works_with_page1_tree'}

def createMacrosInstance(pages):
    from Zope.App.ZMI.StandardMacros import Macros
    class T(Macros):
        def __init__(self, context, request):
            self.context = context
            self.request = request
        macro_pages = pages
    return T(C(), Request())

class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        provideView = getService(None,"Views").provideView
        provideView(I, 'page1', IBrowserPresentation, [page1])
        provideView(I, 'collides_with_page1', IBrowserPresentation,
                    [collides_with_page1])
        provideView(I, 'works_with_page1', IBrowserPresentation,
                    [works_with_page1])

    def testSinglePage(self):
        macros = createMacrosInstance(('page1',))
        self.assertEqual(macros['foo'], 'page1_foo')
        self.assertEqual(macros['bar'], 'page1_bar')
        self.assertRaises(KeyError, macros.__getitem__, 'fish')

    def testConcordentPages(self):
        macros = createMacrosInstance(('page1', 'works_with_page1'))
        self.assertEqual(macros['foo'], 'page1_foo')
        self.assertEqual(macros['bar'], 'page1_bar')
        self.assertEqual(macros['fish'], 'works_with_page1_fish')
        self.assertEqual(macros['tree'], 'works_with_page1_tree')
        self.assertRaises(KeyError, macros.__getitem__, 'pants')
        
    def testConflictingPages(self):
        macros = createMacrosInstance(('page1', 'collides_with_page1'))
        self.assertEqual(macros['foo'], 'page1_foo')
        self.assertEqual(macros['bar'], 'page1_bar')
        self.assertEqual(macros['baz'], 'collides_with_page1_baz')
        self.assertRaises(KeyError, macros.__getitem__, 'pants')

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

