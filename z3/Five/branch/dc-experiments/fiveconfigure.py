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
import warnings
from zope.interface import classImplements
from zope.configuration import xmlconfig
from zope.app.component.interface import provideInterface

from traversable import Traversable

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

def classTraversable(class_):
    # If a class already has this attribute, it means it is either a
    # subclass of api.Traversable or was already processed with this
    # directive; in either case, do nothing... except in the case were
    # the class overrides __bobo_traverse__ instead of getting it from
    # a base class. In this case, we suppose that the class probably
    # didn't bother with the base classes __bobo_traverse__ anyway and
    # we step __fallback_traverse__.
    if (hasattr(class_, '__five_traversable__') and
        not class_.__dict__.has_key('__bobo_traverse__')):
        return

    if hasattr(class_, '__bobo_traverse__'):
        # if there's an existing bobo_traverse hook already, use that
        # as the traversal fallback method
        setattr(class_, "__fallback_traverse__",
                class_.__bobo_traverse__)
    else:
        setattr(class_, "__fallback_traverse__",
                Traversable.__fallback_traverse__)

    setattr(class_, '__bobo_traverse__', Traversable.__bobo_traverse__)
    setattr(class_, '__five_traversable__', True)

def traversable(_context, class_):
    _context.action(
        discriminator = (class_,),
        callable = classTraversable,
        args = (class_,)
        )

def viewable(_context, class_):
    dotted_name = "...%s" % class_.__name__
    warnings.warn('<five:viewable class="%(k)s" /> is deprecated. '
                  'Please switch to <five:traversable class="%(k)s" />' %
                  {'k':dotted_name},
                  DeprecationWarning)
    traversable(_context, class_)
