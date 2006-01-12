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
"""Setup necessary monkey patches and other related logic for using 
regular python packages for zope2 products

$Id$
"""
__author__ = "Rocky Burt"
__all__ = ('setup_python_products',)

import Products
import os
from types import ModuleType

def setup_python_products(context):
    app = context._ProductContext__app
    apply_patches(app)


def apply_patches(app):
    patch_ProductDispatcher__bobo_traverse__(app)
    patch_listDefaultTypeInformation(app)
    patch_externalmethod(app)


# BEGIN MONKEY PATCHES
# Most of these monkey patches were repurposed from the code I 
# wrote for Basket - Rocky

def product_packages(app):
    """Returns all product packages including the regularly defined
    zope2 packages and those without the Products namespace package.
    """
    
    old_product_packages = {}
    for x in dir(Products):
        m = getattr(Products, x)
        if isinstance(m, ModuleType):
            old_product_packages[x] = m
    
    packages = {}
    products = app.Control_Panel.Products
    for product_id in products.objectIds():
        product = products[product_id]
        if hasattr(product, 'package_name'):
            packages[product_id] = __import__(product.package_name)
        elif old_product_packages.has_key(product_id):
            packages[product_id] = old_product_packages[product_id]
    
    return packages
    
def patch_ProductDispatcher__bobo_traverse__(app):
    """Currently, z2's App.FactoryDispatcher.ProductDispatcher only checks
    the Products module for products to look up existing factory dispatchers
    on.  This needs to be fixed to look in all enabled product packages
    as well.
    """
    
    from App.FactoryDispatcher import FactoryDispatcher, ProductDispatcher
    _original__bobo_traverse__ = ProductDispatcher.__bobo_traverse__
    global _original__bobo_traverse__
    
    def __bobo_traverse__(self, REQUEST, name):
        product=self.aq_acquire('_getProducts')()._product(name)

        # Try to get a custom dispatcher from a Python product
        productPkgs = product_packages(app)
        dispatcher_class=getattr(
            productPkgs.get(name, None),
            '__FactoryDispatcher__',
            FactoryDispatcher)

        dispatcher=dispatcher_class(product, self.aq_parent, REQUEST)
        return dispatcher.__of__(self)
    
    ProductDispatcher.__bobo_traverse__ = __bobo_traverse__
    
    


def patch_listDefaultTypeInformation(app):
    """CMF's implementation of listing default type information checks against
    items contained within the import, "import Products".  This needs to
    be extended to check the regular prooduct packages as well.
    """
    
    try:
        from Products.CMFCore.TypesTool import TypesTool
    except ImportError, e:
        # don't continue trying to monkey patch CMF if it doesn't exist
        return
    
    _originalListDefaultTypeInformation = TypesTool.listDefaultTypeInformation
    global _originalListDefaultTypeInformation
    
    from Acquisition import aq_base

    def listDefaultTypeInformation(self):
        # Scans for factory_type_information attributes
        # of all products and factory dispatchers within products.
        res = []
        products = self.aq_acquire('_getProducts')()
        productPkgs = product_packages(app)
        
        for product in products.objectValues():
            product_id = product.getId()

            if hasattr(aq_base(product), 'factory_type_information'):
                ftis = product.factory_type_information
            else:
                package = productPkgs.get(product_id, None)
                dispatcher = getattr(package, '__FactoryDispatcher__', None)
                ftis = getattr(dispatcher, 'factory_type_information', None)

            if ftis is not None:
                if callable(ftis):
                    ftis = ftis()

                for fti in ftis:
                    mt = fti.get('meta_type', None)
                    id = fti.get('id', '')

                    if mt:
                        p_id = '%s: %s (%s)' % (product_id, id, mt)
                        res.append( (p_id, fti) )

        return res
    
    TypesTool.listDefaultTypeInformation = listDefaultTypeInformation


def patch_externalmethod(app):
    """In an effort to make External Methods work with regular python
    packages, this function replaces App.Extensions.getPath with a custom 
    getPath function.  See the getPath doc string for extra details.
    """
    
    from App import Extensions, FactoryDispatcher
    
    _originalGetPath = Extensions.getPath
    global _originalGetPath

    def getPath(prefix, name, checkProduct=1, suffixes=('',)):
        """Make sure to check paths of all registered product packages.
        """

        result = _originalGetPath(prefix, name, checkProduct, suffixes)
        if result is not None:
            return result

        try:
            l = name.find('.')
            if l > 0:
                realName = name[l + 1:]
                toplevel = name[:l]
                
                m = __import__(toplevel)
        
                d = os.path.join(m.__path__[0], prefix, realName)
                for s in suffixes:
                    if s: s="%s.%s" % (d, s)
                    else: s=d
                    if os.path.exists(s): 
                        return s
        except:
            pass
    
    Extensions.getPath = getPath

