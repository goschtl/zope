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

$Id: testStandardMacros.py,v 1.1 2002/10/22 19:34:59 stevea Exp $
"""

import unittest, sys
from Interface import Interface
from Zope.PageTemplate.IMacrosAttribute import IMacrosAttribute
from Zope.App.ZMI.StandardMacros import Macros 

class DummyPageTemplate:

    __implements__ = IMacrosAttribute

    def __init__(self, macros):
        '''macros is a dict for pages'''
        self.macros = macros

page1 = DummyPageTemplate({'foo':'page1_foo', 'bar':'page1_bar'})
collides_with_page1 = DummyPageTemplate({'foo':'collides_with_page1_foo',
                                         'baz':'collides_with_page1_baz'})
works_with_page1 = DummyPageTemplate({'fish':'works_with_page1_fish',
                                      'tree':'works_with_page1_tree'})

class Test(unittest.TestCase):

    def testSinglePage(self):
        from Zope.App.ZMI.StandardMacros import Macros
        class T(Macros):
            macro_pages = (page1,)
        macros = T()
        self.assertEqual(macros['foo'], 'page1_foo')
        self.assertEqual(macros['bar'], 'page1_bar')
        self.assertRaises(KeyError, macros.__getitem__, 'fish')

    def testConcordentPages(self):
        from Zope.App.ZMI.StandardMacros import Macros
        class T(Macros):
            macro_pages = (page1, works_with_page1)
        macros = T()
        self.assertEqual(macros['foo'], 'page1_foo')
        self.assertEqual(macros['bar'], 'page1_bar')
        self.assertEqual(macros['fish'], 'works_with_page1_fish')
        self.assertEqual(macros['tree'], 'works_with_page1_tree')
        self.assertRaises(KeyError, macros.__getitem__, 'pants')
        
    def testConflictingPages(self):
        from Zope.App.ZMI.StandardMacros import Macros
        class T(Macros):
            macro_pages = (page1, collides_with_page1)
        macros = T()
        self.assertEqual(macros['foo'], 'page1_foo')
        self.assertEqual(macros['bar'], 'page1_bar')
        self.assertEqual(macros['baz'], 'collides_with_page1_baz')
        self.assertRaises(KeyError, macros.__getitem__, 'pants')

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

