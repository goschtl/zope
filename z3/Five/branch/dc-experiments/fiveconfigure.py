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
from viewable import Viewable
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
    # subclass of api.Viewable or was already processed with this
    # directive; in either case, do nothing... except in the case were
    # the class overrides the attribute instead of getting it from
    # a base class. In this case, we suppose that the class probably
    # didn't bother with the base classes attribute anyway.
    # If a class already has this attribute, it means it is either a
    # subclass of api.Traversable or was already processed with this
    # directive; in either case, do nothing... except in the case were
    # the class overrides __bobo_traverse__ instead of getting it from
    # a base class. In this case, we suppose that the class probably
    # didn't bother with the base classes __bobo_traverse__ anyway and
    # we step __fallback_traverse__.
    if (hasattr(class_, '__five_traversable__') and
        hasattr(class_, '__dict__') and
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
        discriminator = ('five:traversable', class_,),
        callable = classTraversable,
        args = (class_,)
        )

def viewable(_context, class_):
    dotted_name = "...%s" % class_.__name__
    warnings.warn('<five:viewable class="%(k)s" /> has changed meaning. '
                  'Please switch to <five:traversable class="%(k)s" />'
                  'unless you know what you are doing.' %
                  {'k':dotted_name},
                  DeprecationWarning)
    _context.action(
        discriminator = ('five:viewable', class_,),
        callable = classViewable,
        args = (class_,)
        )

def classViewable(class_):
    # If a class already has this attribute, it means it is either a
    # subclass of api.Viewable or was already processed with this
    # directive; in either case, do nothing... except in the case were
    # the class overrides the attribute instead of getting it from
    # a base class. In this case, we suppose that the class probably
    # didn't bother with the base classes attribute anyway.
    if (hasattr(class_, '__five_viewable__') and
        hasattr(class_, '__dict__') and
        (not class_.__dict__.has_key('__browser_default__') and
         not class_.__dict__.has_key('__call__') and
         not class_.__dict__.has_key('index_html'))):
        return

    if not hasattr(class_, '__dict__'):
        # XXX Should raise an error maybe?
        return

    if class_.__dict__.has_key('__browser_default__'):
        # if there's an existing __browser_default__ hook already, use that
        # as the fallback
        setattr(class_, "__fallback_default__",
                class_.__browser_default__)
    else:
        setattr(class_, "__fallback_default__",
                Viewable.__fallback_default__)

    if class_.__dict__.has_key('index_html'):
        # if there's an existing index_html already, use that
        # as the fallback
        setattr(class_, "fallback_index_html__",
                class_.index_html)
    else:
        setattr(class_, "fallback_index_html__",
                Viewable.fallback_index_html__)

    if class_.__dict__.has_key('__call__'):
        # if there's an existing __call__ already, use that
        # as the fallback
        setattr(class_, "fallback_call__",
                class_.__call__)
    else:
        setattr(class_, "fallback_call__",
                Viewable.fallback_call__)


    setattr(class_, '__browser_default__', Viewable.__browser_default__)
    setattr(class_, '__call__', Viewable.__call__)
    setattr(class_, 'index_html', Viewable.index_html)
    setattr(class_, '__five_viewable__', True)

