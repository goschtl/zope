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
framework and the db-api connection. Databases which
want to support sub transactions need to implement their own
proxy. 

$Id: ZopeDBTransactionManager.py,v 1.2 2002/07/10 23:37:26 srichter Exp $
"""
from Transaction.IDataManager import IDataManager

class ZopeDBTransactionManager:

    __implements__ =  IDataManager

    def __init__(self, dbconn):
        """Callback is a function invoked when the transaction is finished.
        """
        self.dbconn = dbconn
        self._vote = 0

    ############################################################
    # Implementation methods for interface
    # Zope.Transaction.IDataManager.

    def abort(self, *ignored):
        'See Transaction.IDataManager.IDataManager'
        try:
            self.dbconn.rollback()
        finally:
            self.dbconn.unregisterFromTxn()

    def commit(self, *ignored):
        'See Transaction.IDataManager.IDataManager'

    def tpc_vote(self, *ignored):
        'See Transaction.IDataManager.IDataManager'
        self._vote = 1
        
    def tpc_begin(self, *ignored):
        'See Transaction.IDataManager.IDataManager'

    def tpc_finish(self, *ignored):
        'See Transaction.IDataManager.IDataManager'
        if self._vote:
            try:
                self.dbconn.commit()
            finally:
                self.dbconn.unregisterFromTxn()
        
    tpc_abort = abort
    
    #
    ############################################################




