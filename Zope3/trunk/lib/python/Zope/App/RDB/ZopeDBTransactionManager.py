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
""" Zope RDBMS Transaction Integration.

Provides a proxy for interaction between the zope transaction
framework and the db-api connection. Databases which want to support
sub transactions need to implement their own proxy.

$Id: ZopeDBTransactionManager.py,v 1.5 2002/12/20 19:10:38 jeremy Exp $
"""
from Transaction.interfaces import IDataManager

class ZopeDBTransactionManager:

    __implements__ =  IDataManager

    def __init__(self, dbconn):
        self._dbconn = dbconn

    def prepare(self, txn):
        return True

    def abort(self, txn):
        self._dbconn.rollback()

    def commit(self, txn):
        self._dbconn.commit()

    # XXX Do any of the Python DB-API implementations support
    # two-phase commit?

    def savepoint(self, txn):
        return None
