##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Five-specific directive handlers

These directives are specific to Five and have no equivalents in Zope 3.

$Id$
"""
import os
from zope.interface import classImplements
from zope.configuration import xmlconfig
from zope.app.component.interface import provideInterface

from viewable import Viewable

def findProducts():
    import Products
    from types import ModuleType
    products = []
    for name in dir(Products):
        product = getattr(Products, name)
        if isinstance(product, ModuleType):
            products.append(product)
    return products

def loadProducts(_context):
    products = findProducts()

    # first load meta.zcml files
    for product in products:
        zcml = os.path.join(os.path.dirname(product.__file__), "meta.zcml")
        if os.path.isfile(zcml):
            xmlconfig.include(_context, zcml, package=product)

    # now load their configure.zcml
    for product in products:
        zcml = os.path.join(os.path.dirname(product.__file__), "configure.zcml")
        if os.path.isfile(zcml):
            xmlconfig.include(_context, zcml, package=product)

def loadProductsOverrides(_context):
    for product in findProducts():
        zcml = os.path.join(os.path.dirname(product.__file__), "overrides.zcml")
        if os.path.isfile(zcml):
            xmlconfig.includeOverrides(_context, zcml, package=product)

def implements(_context, class_, interface):
    for interface in interface:
        _context.action(
            discriminator = None,
            callable = classImplements,
            args = (class_, interface)
            )
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (interface.__module__ + '.' + interface.getName(),
                    interface)
            )

def classViewable(class_):
    if hasattr(class_, '__bobo_traverse__'):
        raise TypeError("__bobo_traverse already__ exists on %s" % class_)
    setattr(class_, '__bobo_traverse__', Viewable.__bobo_traverse__)

def viewable(_context, class_):
    _context.action(
        discriminator = (class_,),
        callable = classViewable,
        args = (class_,)
        )
