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
__all__ = ('setup_python_products', 'register_python_product')

import os
import types

import Products
from App.Product import initializeProduct
from App.ProductContext import ProductContext

_zope_app = None

def registerProduct(_context, package):
    """ZCML directive function for registering a python package product
    """
    
    _context.action(
        discriminator = ('registerProduct',),
        callable = register_python_product,
        args = (package,)
        )


def register_python_product(package):
    """Registers the given python package as a Zope 2 style product
    """
    
    if isinstance(package, basestring):
        module_ = __import__(package)
    elif isinstance(package, types.ModuleType):
        module_ = package
    else:
        raise TypeError("The package argument must either be an instance of " \
                        +"basestring or types.ModuleType")

    if not hasattr(module_, 'initialize'):
        raise ValueError("The module '%s' requires a Zope 2 style " \
                         +"initialize function" % module_.__name__)

    product = initializeProduct(module_, 
                                module_.__name__, 
                                module_.__path__[0], 
                                _zope_app)

    product.package_name = module_.__name__

    newContext = ProductContext(product, _zope_app, module_)
    module_.initialize(newContext)

def setup_python_products(context):
    """Initialize the python-packages-as-products logic
    """
    
    _zope_app = context._ProductContext__app
    global _zope_app
    apply_patches(_zope_app)


def apply_patches(app):
    """Apply necessary monkey patches to force Zope 2 to be capable of
    handling "products" that are not necessarily located under the Products
    package.  Ultimately all functionality provided by these patches should
    be folded into Zope 2 core.
    """
    
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
        if isinstance(m, types.ModuleType):
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
    from Products.ExternalMethod import ExternalMethod
    
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
    ExternalMethod.getPath = getPath
