##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""
$Id: ZopeConnection.py,v 1.2 2002/07/10 23:37:26 srichter Exp $
"""
from IZopeConnection import IZopeConnection
from IZopeCursor import IZopeCursor
from ZopeCursor import ZopeCursor
from ZopeDBTransactionManager import ZopeDBTransactionManager
from Transaction import get_transaction


class ZopeConnection:

    __implements__ =  IZopeConnection

    def __init__(self, conn):
        self.conn = conn
        # flag for txn registration status
        self._txn_registered = 0

    def __getattr__(self, key):
        # The IDBIConnection interface is hereby implemented
        return self.__dict__.get(key, getattr(self.conn, key))

    ############################################################
    # Implementation methods for interface
    # Zope/App/RDB/IZopeConnection.py

    def cursor(self):
        'See Zope.App.RDB.IZopeConnection.IZopeConnection'
        return ZopeCursor(self.conn.cursor(), self)

    def registerForTxn(self):
        'See Zope.App.RDB.IZopeConnection.IZopeConnection'
        if not self._txn_registered:
            tm = ZopeDBTransactionManager(self)
            t = get_transaction()
            t.register(tm)
            self._txn_registered = 1

    def unregisterFromTxn(self):
        'See Zope.App.RDB.IZopeConnection.IZopeConnection'
        self._txn_registered = 0

    ######################################
    # from: Zope.App.RDB.IDBITypeInfoProvider.IDBITypeInfoProvider

    def getTypeInfo(self):
        'See Zope.App.RDB.IDBITypeInfoProvider.IDBITypeInfoProvider'
        # Stubbed for now
        
    #
    ############################################################
