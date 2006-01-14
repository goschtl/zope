##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Python packages-as-products testing

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_registerProduct():
    """
    Testing registerProduct

      >>> from zope.app.testing.placelesssetup import setUp, tearDown
      >>> setUp()
      >>> import Products
      >>> import Products.Five
      >>> import Products.Five.tests
      >>> import Products.Five.tests.testing
      >>> from Products.Five.tests.testing import zope2module
      >>> from Products.Five import pythonproducts
    
    Make sure registerProduct only handles appropriate types::
    
      >>> pythonproducts.register_python_product(None)
      Traceback (most recent call last):
      ...
      TypeError: The package argument must either be an instance of basestring or types.ModuleType

      >>> pythonproducts.register_python_product(zope2module)
      Traceback (most recent call last):
      ...
      ValueError: Registering a python package currently only supports filesystem based pure python packages
                  
    
    Clean up:

      >>> tearDown()
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()
