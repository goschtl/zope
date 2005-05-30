##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
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
from Products.Five.testing import manage_addFiveTraversableFolder

class StandardMacrosTests(ZopeTestCase):

    def afterSetUp(self):
        zcml.load_config('configure.zcml', package=Products.Five.skin.tests)
        uf = self.folder.acl_users
        uf._doAddUser('manager', 'r00t', ['Manager'], [])
        self.login('manager')
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
