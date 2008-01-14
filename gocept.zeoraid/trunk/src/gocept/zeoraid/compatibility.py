# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Compatibility layers."""

import zope.interface
import zope.component
import zope.proxy
import zope.proxy.decorator

import ZODB.utils
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
        lt = zope.proxy.getProxiedObject(self)._server.lastTransaction()
        if lt is None:
            lt = ZODB.utils.z64
        return lt


compatibility_initialized = False


def setup():
    global compatibility_initialized
    if compatibility_initialized:
        return
    zope.component.provideAdapter(ClientStorage38)
    compatibility_initialized = True
