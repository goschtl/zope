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
$Id: ZopeConnection.py,v 1.1 2002/06/25 15:41:45 k_vertigo Exp $
"""
from IZopeConnection import IZopeConnection
from IZopeCursor import IZopeCursor
from ZopeCursor import ZopeCursor
from ZopeDBTransactionManager import ZopeDBTransactionManager
from Transaction import get_transaction

class ZopeConnection:

    __implements__ = IZopeConnection

    def __init__(self, conn):
        self.conn = conn
        # flag for txn registration status
        self._txn_registered = 0

    def cursor(self):
        """Returns an IZopeCursor"""
        return ZopeCursor(self.conn.cursor(), self)

    def registerForTxn(self):
        
        if self._txn_registered:
            return

        tm = ZopeDBTransactionManager(self)
        t = get_transaction()
        t.register(tm)
        self._txn_registered = 1
        
    def unregisterFromTxn(self):
        self._txn_registered = 0
        
    def __getattr__(self, key):
        return getattr(self.conn, key)

    def getTypeInfo(self):
        # Stubbed for now
        pass




