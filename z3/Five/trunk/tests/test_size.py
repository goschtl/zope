##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
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
