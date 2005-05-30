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
"""Size adapters for testing

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import ZopeTestCase, installProduct
installProduct('Five')

import Products.Five.tests
from Products.Five import zcml
from Products.Five.tests.simplecontent import manage_addSimpleContent
from Products.Five.tests.fancycontent import manage_addFancyContent

class SizeTest(ZopeTestCase):

    def afterSetUp(self):
	zcml.load_config('size.zcml', package=Products.Five.tests)

    def test_no_get_size_on_original(self):
        manage_addSimpleContent(self.folder, 'simple', 'Simple')
	obj = self.folder.simple
	self.assertEquals(obj.get_size(), 42)

    def test_get_size_on_original_and_fallback(self):
	manage_addFancyContent(self.folder, 'fancy', 'Fancy')
	obj = self.folder.fancy
	self.assertEquals(obj.get_size(), 43)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SizeTest))
    return suite

if __name__ == '__main__':
    framework()
