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
from bridge import fromZ2Interface

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
    # if a class already has this attribute, it means it is either a
    # subclass of api.Viewable or was already processed with this
    # directive; in either case, do nothing...
    if hasattr(class_, '__five_viewable__'):
        return

    if hasattr(class_, '__bobo_traverse__'):
        # if there's an existing bobo_traverse hook already, use that
        # as the traversal fallback method
        setattr(class_, "__fallback_traverse__", class_.__bobo_traverse__)
    else:
        setattr(class_, "__fallback_traverse__", Viewable.__fallback_traverse__)

    setattr(class_, '__bobo_traverse__', Viewable.__bobo_traverse__)
    setattr(class_, '__five_viewable__', True)

def viewable(_context, class_):
    _context.action(
        discriminator = (class_,),
        callable = classViewable,
        args = (class_,)
        )

def createZope2Bridge(zope2, package, name):
    # Map a Zope 2 interface into a Zope3 interface, seated within 'package'
    # as 'name'.
    z3i = fromZ2Interface(zope2)

    if name is not None:
        z3i.__dict__['__name__'] = name

    z3i.__dict__['__module__'] = package.__name__
    setattr(package, z3i.getName(), z3i)

def bridge(_context, zope2, package, name=None):
    # Directive handler for <five:bridge> directive.

    # N.B.:  We have to do the work early, or else we won't be able
    #        to use the synthesized interface in other ZCML directives.
    createZope2Bridge(zope2, package, name)

    # Faux action, only for conflict resolution.
    _context.action(
        discriminator = (zope2,),
        )
