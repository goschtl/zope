##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Test standard macros

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import ZopeTestCase, installProduct
installProduct('Five')

import glob
import Products.Five.skin.tests
from Products.Five import zcml
from Products.Five.tests.helpers import manage_addFiveTraversableFolder

class StandardMacrosTests(ZopeTestCase):

    def afterSetUp(self):
	zcml.load_config('configure.zcml', package=Products.Five.skin.tests)
	manage_addFiveTraversableFolder(self.folder, 'testoid', 'Testoid')

    def test_standard_macros(self):
        view = self.folder.unrestrictedTraverse('testoid/@@fivetest_macros')
        self.assertRaises(KeyError, view.__getitem__, 'non-existing-macro')
        self.failUnless(view['birdmacro'])
        self.failUnless(view['dogmacro'])
        # Test aliases
        self.failUnless(view['flying'])
        self.failUnless(view['walking'])
        self.assertEquals(view['flying'], view['birdmacro'])
        self.assertEquals(view['walking'], view['dogmacro'])
        # Test traversal
        base = 'testoid/@@fivetest_macros/%s'
        for macro in ('birdmacro', 'dogmacro',
                      'flying', 'walking'):
            view = self.folder.unrestrictedTraverse(base % macro)
        self.failUnless(view)

    def test_macro_access(self):
        view = self.folder.unrestrictedTraverse('testoid/seagull.html')
        self.assertEquals('<html><head><title>bird macro</title></head><body>Color: gray</body></html>\n', view())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StandardMacrosTests))
    return suite

if __name__ == '__main__':
    framework()
