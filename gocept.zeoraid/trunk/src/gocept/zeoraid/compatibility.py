# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Compatibility layers."""

import zope.interface
import zope.component
import zope.proxy
import zope.proxy.decorator

import ZEO.ClientStorage

import gocept.zeoraid.interfaces
import gocept.zeoraid.utils


class ClientStorage38(zope.proxy.decorator.SpecificationDecoratorBase):
    """Compatibility layer for the ClientStorage of ZODB 3.8.

    Includes fixes for:

        - lastTransaction: uses the _cache incorrectly to determine the last
          transaction.

    """

    zope.component.adapts(
        ZEO.ClientStorage.ClientStorage)
    zope.interface.implements(
        gocept.zeoraid.interfaces.IRAIDCompatibleStorage)

    @zope.proxy.non_overridable
    def lastTransaction(self):
        return zope.proxy.getProxiedObject(self)._server.lastTransaction()


compatibility_matrix = {
    '3.8': ClientStorage38
}


compatibility_initialized = False


def setup():
    global compatibility_initialized
    if compatibility_initialized:
        return
    zodb_version = gocept.zeoraid.utils.guess_zodb_version()
    gocept.zeoraid.utils.logger.info(
        'Setting up compatibility layer for ZODB %s.' % zodb_version)
    storage_adapter = compatibility_matrix[zodb_version]
    zope.component.provideAdapter(storage_adapter)
    compatibility_initialized = True
