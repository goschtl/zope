##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Boiler plate test module

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

# uncomment any of these if your test needs to deal with either
# FiveTraversableFolder/SimpleContent/FancyContent
#from Products.Five.testing import manage_addFiveTraversableFolder
#from Products.Five.tests.simplecontent import manage_addSimpleContent
#from Products.Five.tests.fancycontent import manage_addFancyContent

class BoilerPlateTest(ZopeTestCase):

    def afterSetUp(self):
        zcml.load_config('boilertest.zcml', package=Products.Five.tests)
        # uncomment any of these if your test needs to deal with either
        # FiveTraversableFolder/SimpleContent/FancyContent
        #manage_addFiveTraversableFolder(self.folder, 'testoid', 'Testoid')
        #manage_addSimpleContent(self.folder, 'simple', 'Simple')
        #manage_addFancyContent(self.folder, 'fancy', 'Fancy')

    def test_boiler_plate(self):
        pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BoilerPlateTest))
    return suite

if __name__ == '__main__':
    framework()
