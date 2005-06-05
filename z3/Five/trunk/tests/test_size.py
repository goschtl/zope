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
from Testing.ZopeTestCase import ZopeDocTestSuite, installProduct
installProduct('Five')

def setUpSize(self):
    import Products.Five.tests
    from Products.Five import zcml
    zcml.load_config('size.zcml', package=Products.Five.tests)
    
def test_size():
    """Test size adapters

      >>> from Products.Five.tests.simplecontent import manage_addSimpleContent
      >>> from Products.Five.tests.fancycontent import manage_addFancyContent

    We have registered an ``ISized`` adapter for SimpleContent:

      >>> n = manage_addSimpleContent(self.folder, 'simple', 'Simple')
      >>> self.folder.simple.get_size()
      42

    Fancy content already has a ``get_size`` method

      >>> n = manage_addFancyContent(self.folder, 'fancy', 'Fancy')
      >>> self.folder.fancy.get_size()
      43
    """

def test_suite():
    return unittest.TestSuite((
            ZopeDocTestSuite(setUp=setUpSize),
            ))

if __name__ == '__main__':
    framework()
