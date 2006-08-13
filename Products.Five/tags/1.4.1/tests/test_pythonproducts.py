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
"""Unit tests for the registerPackage directive.

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# need to add the testing package to the pythonpath in order to
# test python-packages-as-products
from Products.Five.tests import testing
sys.path.append(testing.__path__[0])

def test_aRegisterPackageCall():
    """
    Testing registerPackage.  Recently renamed method to something to
    would produce an out of order issue that breaks the test.

      >>> from zope.app.testing.placelesssetup import setUp, tearDown
      >>> setUp()
      >>> import Products
      >>> import Products.Five
      >>> from Products.Five import zcml
      >>> from Products.Five import pythonproducts
      >>> zcml.load_config('meta.zcml', Products.Five)
      >>> pythonproducts.setupPythonProducts(app)

    Make sure a python package with no initialize (even though one
    is specified) will fail::
    
      >>> configure_zcml = '''
      ... <configure
      ...     xmlns="http://namespaces.zope.org/zope"
      ...     xmlns:five="http://namespaces.zope.org/five"
      ...     i18n_domain="foo">
      ...   <five:registerPackage
      ...       package="pythonproduct1"
      ...       initialize="pythonproduct1.initialize"
      ...       />
      ... </configure>'''
      >>> zcml.load_string(configure_zcml)
      Traceback (most recent call last):
          ...
      ZopeXMLConfigurationError: ...
      ConfigurationError: ('...pythonproduct1 has no global initialize')    

    Make sure a python package with a valid initialize gets its
    initialize function called::
    
      >>> configure_zcml = '''
      ... <configure
      ...     xmlns="http://namespaces.zope.org/zope"
      ...     xmlns:five="http://namespaces.zope.org/five"
      ...     i18n_domain="foo">
      ...   <five:registerPackage
      ...       package="pythonproduct2"
      ...       initialize="pythonproduct2.initialize"
      ...       />
      ... </configure>'''
      >>> zcml.load_string(configure_zcml)
      pythonproduct2 initialized
      
    Test to see if the pythonproduct2 python package actually gets setup
    as a zope2 product in the Control Panel.

      >>> productListing = app.Control_Panel.Products.objectIds()
      >>> 'pythonproduct2' in productListing
      True

    Clean up:

      >>> tearDown()
    """

def test_externalmethods():
    """
    Testing registerPackage

      >>> from zope.app.testing.placelesssetup import setUp, tearDown
      >>> setUp()
      >>> import Products
      >>> import Products.Five
      >>> from Products.Five import zcml
      >>> from Products.Five import pythonproducts
      >>> zcml.load_config('meta.zcml', Products.Five)
      >>> pythonproducts.setupPythonProducts(app)

      >>> configure_zcml = '''
      ... <configure
      ...     xmlns="http://namespaces.zope.org/zope"
      ...     xmlns:five="http://namespaces.zope.org/five"
      ...     i18n_domain="foo">
      ...   <five:registerPackage
      ...       package="pythonproduct2"
      ...       initialize="pythonproduct2.initialize"
      ...       />
      ... </configure>'''
      >>> zcml.load_string(configure_zcml)
      pythonproduct2 initialized
      
    Lets go ahead and try setting up an external method from the
    pythonproduct2 product.
    
      >>> from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
      >>> manage_addExternalMethod(app, 'testexternal', '', 'pythonproduct2.somemodule', 'somemethod')
      
    Now lets actually execute the external method.
        
      >>> app.testexternal()
      Executed somemethod

    Clean up:

      >>> tearDown()
    """


def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()
