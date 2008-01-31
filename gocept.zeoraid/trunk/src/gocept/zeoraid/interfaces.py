# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Interface descriptions"""


import zope.interface

import ZEO.ClientStorage


class RAIDError(Exception):
    pass


class RAIDClosedError(RAIDError, ZEO.ClientStorage.ClientStorageError):
    pass


class IRAIDStorage(zope.interface.Interface):
    """A ZODB storage providing simple RAID capabilities."""

    def raid_status():
        pass

    def raid_details():
        pass

    def raid_disable(name):
        pass

    def raid_recover(name):
        pass
