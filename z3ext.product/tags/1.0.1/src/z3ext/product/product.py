##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""

$Id: product.py 1843 2008-03-25 18:39:00Z fafhrd91 $
"""
from BTrees.OOBTree import OOBTree

from zope import interface, event
from zope.component import getSiteManager
from zope.component import getUtility, queryUtility, getUtilitiesFor

from z3c.configurator import configure

import z3ext.product
from z3ext.controlpanel.configlettype import ConfigletProperty

from z3ext.product.i18n import _
from z3ext.product import interfaces
from z3ext.product.interfaces import IProduct, IProductExtension


class Product(object):
    """ base product class """
    interface.implements(IProduct)

    __installed__ = ConfigletProperty(IProduct['__installed__'])

    def install(self):
        if self.__installed__:
            raise interfaces.ProductAlreadyInstalledError(
                _('Product already installed.'))

        self.__installed__ = True
        self.update()

        sm = getSiteManager()

        registry = getattr(z3ext.product, self.__product_name__)
        if registry not in sm.__bases__:
            sm.__bases__ = (registry,) + sm.__bases__

        event.notify(interfaces.ProductInstalledEvent(self.__product_name__, self))

    def update(self):
        if not self.__installed__:
            raise interfaces.ProductNotInstalledError(
                _('Product not installed.'))

        configure(self, {})

        site = getSiteManager()
        registry = getattr(z3ext.product, self.__product_name__)
        if registry not in site.__bases__:
            site.__bases__ = (registry,) + site.__bases__

        event.notify(interfaces.ProductUpdatedEvent(
            self.__product_name__, self))

    def uninstall(self):
        for name, ext in self.items():
            if IProductExtension.providedBy(ext) and ext.__installed__:
                ext.uninstall()

        if not self.__installed__:
            raise interfaces.ProductNotInstalledError(
                _('Product not installed.'))

        self.__installed__ = False

        site = getSiteManager()
        registry = getattr(z3ext.product, self.__product_name__)

        if registry in site.__bases__:
            bases = list(site.__bases__)
            bases.remove(registry)
            site.__bases__ = tuple(bases)

        event.notify(interfaces.ProductUninstalledEvent(
            self.__product_name__, self))

    def isInstalled(self):
        return self.__installed__

    def listExtensions(self):
        exts = []
        for name, ext in self.items():
            if IProductExtension.providedBy(ext):
                exts.append(name)

        return exts


class ProductExtension(Product):
    interface.implements(IProductExtension)

    def install(self):
        if not self.__parent__.__installed__:
            raise interfaces.ProductNotInstalledError(
                self.__parent__.__product_name__)
        super(ProductExtension, self).install()

    def update(self):
        if not self.__parent__.__installed__:
            raise interfaces.ProductNotInstalledError(
                self.__parent__.__product_name__)
        super(ProductExtension, self).update()

    def isInstalled(self):
        if self.__parent__.__installed__:
            return self.__installed__
        else:
            return False
