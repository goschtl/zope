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

$Id: test_standardmacros.py,v 1.2 2002/12/25 14:12:41 jim Exp $
"""

import unittest, sys
from zope.app.services.tests.placefulsetup\
           import PlacefulSetup
from zope.component import getService
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.interface import Interface
from zope.app.browser.skins.basic.standardmacros import Macros


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
    from zope.app.browser.skins.basic.standardmacros import Macros
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
