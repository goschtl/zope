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

from z3ext.product import interfaces
from z3ext.product.interfaces import _, IProduct, IProductExtension


class Product(object):
    """ base product class """
    interface.implements(IProduct)

    @property
    def __installed__(self):
        sm = getSiteManager()

        registry = getattr(z3ext.product, self.__product_name__)
        return registry in sm.__bases__

    def _checkRequiredInstall(self):
        for productId in self.__required__:
            product = queryUtility(IProduct, productId)
            if product is None:
                raise interfaces.RequiredProductNotFound(
                    _('Required product is not found.'))
            if not product.__installed__:
                product.install()

    def _checkRequiredUpdate(self):
        for productId in self.__required__:
            product = queryUtility(IProduct, productId)
            if product is None:
                raise interfaces.RequiredProductNotFound(
                    _('Required product is not found.'))
            if not product.__installed__:
                product.install()
            else:
                product.update()

    def install(self):
        self._checkRequiredInstall()
        
        if self.__installed__:
            raise interfaces.ProductAlreadyInstalledError(
                _('Product already installed.'))

        sm = getSiteManager()

        registry = getattr(z3ext.product, self.__product_name__)
        sm.__bases__ = (registry,) + sm.__bases__

        event.notify(interfaces.ProductInstalledEvent(self.__product_name__, self))

        self.update()

    def update(self):
        if not self.__installed__:
            raise interfaces.ProductNotInstalledError(
                _('Product is not installed.'))

        configure(self, {})
        event.notify(
            interfaces.ProductUpdatedEvent(self.__product_name__, self))

        self._checkRequiredUpdate()

    def uninstall(self):
        for name, ext in self.items():
            if IProductExtension.providedBy(ext) and ext.__installed__:
                ext.uninstall()

        if not self.__installed__:
            raise interfaces.ProductNotInstalledError(
                _('Product is not installed.'))

        sm = getSiteManager()
        registry = getattr(z3ext.product, self.__product_name__)

        bases = list(sm.__bases__)
        bases.remove(registry)
        sm.__bases__ = tuple(bases)

        event.notify(
            interfaces.ProductUninstalledEvent(self.__product_name__, self))

    def _checkInstalled(self, sm, registry, seen):
        if sm in seen:
            return False
        seen.add(sm)

        if registry in sm.__bases__:
            return True

        for reg in sm.__bases__:
            if self._checkInstalled(reg, registry, seen):
                return True

        return False

    def isInstalled(self):
        sm = getSiteManager()
        registry = getattr(z3ext.product, self.__product_name__)
        seen = set()
        return self._checkInstalled(sm, registry, seen)

    def listExtensions(self):
        exts = []
        for name, ext in self.items():
            if IProductExtension.providedBy(ext):
                exts.append(name)

        return exts

    def isUninstallable(self):
        sm = getSiteManager()
        registry = getattr(z3ext.product, self.__product_name__)
        return registry in sm.__bases__


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
