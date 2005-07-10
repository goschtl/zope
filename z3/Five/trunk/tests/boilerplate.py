##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
#from Products.Five.testing.simplecontent import manage_addSimpleContent
#from Products.Five.testing.fancycontent import manage_addFancyContent

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
