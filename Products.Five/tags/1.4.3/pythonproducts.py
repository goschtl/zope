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
"""Setup necessary monkey patches and other related logic for using 
regular python packages for zope2 products

$Id$
"""
__author__ = "Rocky Burt"

import os
import types

import Products
from App.Product import initializeProduct
from App.ProductContext import ProductContext
from zope.testing import cleanup
import Zope2

def isMonkeyPatched(m):
    return hasattr(m, '__five_method__')  

def setupPythonProducts(appOrContext):
    """Initialize the python-packages-as-products logic
    """
    
    applyPatches()


def applyPatches():
    """Apply necessary monkey patches to force Zope 2 to be capable of
    handling "products" that are not necessarily located under the Products
    package.  Ultimately all functionality provided by these patches should
    be folded into Zope 2 core.
    """
    
    patch_ProductDispatcher__bobo_traverse__()
    patch_externalmethod()

def removePatches():
    """Remove all monkey patches.
    """
   
    from App.FactoryDispatcher import FactoryDispatcher, ProductDispatcher
    from App import Extensions   
    from Products.ExternalMethod import ExternalMethod
    
    if isMonkeyPatched(ProductDispatcher.__bobo_traverse__):
        ProductDispatcher.__bobo_traverse__ = _original__bobo_traverse__

    if isMonkeyPatched(Extensions.getPath):
        Extensions.getPath = _originalGetPath
        ExternalMethod.getPath = _originalGetPath

cleanup.addCleanUp(removePatches)

# BEGIN MONKEY PATCHES
# Most of these monkey patches were repurposed from the code I 
# wrote for Basket - Rocky

def product_packages():
    """Returns all product packages including the regularly defined
    zope2 packages and those without the Products namespace package.
    """

    old_product_packages = {}
    for x in dir(Products):
        m = getattr(Products, x)
        if isinstance(m, types.ModuleType):
            old_product_packages[x] = m
    
    packages = {}
    app = Zope2.app()
    try:
        products = app.Control_Panel.Products
        for product_id in products.objectIds():
            product = products[product_id]
            if hasattr(product, 'package_name'):
                pos = product.package_name.rfind('.')
                if pos > -1:
                    packages[product_id] = __import__(product.package_name, 
                                                      globals(), {}, 
                                                      product.package_name[pos+1:])
                else:
                    packages[product_id] = __import__(product.package_name)
            elif old_product_packages.has_key(product_id):
                packages[product_id] = old_product_packages[product_id]
    finally:
        app._p_jar.close()
    
    return packages
    
def patch_ProductDispatcher__bobo_traverse__():
    """Currently, z2's App.FactoryDispatcher.ProductDispatcher only checks
    the Products module for products to look up existing factory dispatchers
    on.  This needs to be fixed to look in all enabled product packages
    as well.
    """
    
    from App.FactoryDispatcher import FactoryDispatcher, ProductDispatcher
    
    if isMonkeyPatched(ProductDispatcher.__bobo_traverse__):
        return
    
    global _original__bobo_traverse__
    _original__bobo_traverse__ = ProductDispatcher.__bobo_traverse__
    
    def __bobo_traverse__(self, REQUEST, name):
        product=self.aq_acquire('_getProducts')()._product(name)

        # Try to get a custom dispatcher from a Python product
        productPkgs = product_packages()
        dispatcher_class=getattr(
            productPkgs.get(name, None),
            '__FactoryDispatcher__',
            FactoryDispatcher)

        dispatcher=dispatcher_class(product, self.aq_parent, REQUEST)
        return dispatcher.__of__(self)
    __bobo_traverse__.__five_method__ = True
    
    ProductDispatcher.__bobo_traverse__ = __bobo_traverse__
    

def patch_externalmethod():
    """In an effort to make External Methods work with regular python
    packages, this function replaces App.Extensions.getPath with a custom 
    getPath function.  See the getPath doc string for extra details.
    """
    
    from App import Extensions, FactoryDispatcher
    from Products.ExternalMethod import ExternalMethod

    if isMonkeyPatched(Extensions.getPath):
        return
    
    global _originalGetPath
    _originalGetPath = Extensions.getPath

    def getPath(prefix, name, checkProduct=1, suffixes=('',)):
        """Make sure to check paths of all registered product packages.
        """

        result = _originalGetPath(prefix, name, checkProduct, suffixes)
        if result is not None:
            return result

        try:
            l = name.rfind('.')
            if l > 0:
                realName = name[l + 1:]
                toplevel = name[:l]
                
                pos = toplevel.rfind('.')
                if pos > -1:
                    m = __import__(toplevel, globals(), {}, toplevel[pos+1:])
                else:
                    m = __import__(toplevel)
        
                d = os.path.join(m.__path__[0], prefix, realName)
                
                for s in suffixes:
                    if s: s="%s.%s" % (d, s)
                    else: s=d
                    if os.path.exists(s): 
                        return s
        except:
            pass
    
    getPath.__five_method__ = True

    Extensions.getPath = getPath
    ExternalMethod.getPath = getPath
