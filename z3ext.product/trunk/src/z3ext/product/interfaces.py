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
""" z3ext.product interfaces

$Id: interfaces.py 1843 2008-03-25 18:39:00Z fafhrd91 $
"""
from zope import schema, interface
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('z3ext')


class ProductError(Exception):
    """ base error class for product management """


class ProductNotInstalledError(ProductError):
    """ """


class ProductAlreadyInstalledError(ProductError):
    """ """


class InvalidProduct(ProductError):
    """ """


class ProductWarningError(ProductError):
    """ dependencies error """


class RequiredProductNotFound(ProductError):
    """ """


class IProduct(interface.Interface):
    """ product information """

    __product_name__ = schema.TextLine(
        title = u'Product name',
        required = True)

    __required__ = interface.Attribute(u'Required products.')

    __installed__ = interface.Attribute(u'Is product installed.')

    def install():
        """ install and configure product """

    def uninstall():
        """ uninstall product """

    def update():
        """ update product """

    def isInstalled():
        """ is product installed """

    def listExtensions():
        """ list IProductExtension for this product """

    def isUninstallable():
        """ is product uninstallable """
        

class IProductExtension(interface.Interface):
    """ product extension """


class IProductInstaller(interface.Interface):
    """ installer for external products """


class IAbstractProductEvent(interface.Interface):
    """ base event interface """

    id = schema.TextLine(
        title = u'Product id',
        required = True)

    product = interface.Attribute('IProduct object')


class IProductInstalledEvent(IAbstractProductEvent):
    """ new product installed """


class IProductUninstalledEvent(IAbstractProductEvent):
    """ product uninstalled """


class IProductUpdatedEvent(IAbstractProductEvent):
    """ product updated """


class AbstractProductEvent(object):

    def __init__(self, id, product):
        self.id = id
        self.product = product


class ProductInstalledEvent(AbstractProductEvent):
    interface.implements(IProductInstalledEvent)


class ProductUninstalledEvent(AbstractProductEvent):
    interface.implements(IProductUninstalledEvent)


class ProductUpdatedEvent(AbstractProductEvent):
    interface.implements(IProductUpdatedEvent)
