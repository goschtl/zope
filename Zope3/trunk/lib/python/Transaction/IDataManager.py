##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
try:
    from Interface import Interface
except ImportError:
    class Interface: pass


class IDataManager(Interface):
    """Data management interface for storing objects transactionally

    This is currently implemented by ZODB database connections.
    """

    def abort(object, transaction):
        """Abort changes made to an object in a transaction"""
    
    def tpc_begin(transaction, subtransaction=0):
        """Begin two-phase commit of a transaction

        If a non-zero subtransaction flag is provided, then begin a
        sub-transaction.
        """
        
    def commit(object, transaction):
        """Commit (tentatively) changes made to an object in a transaction

        This method is called during the first stage of a two-phase commit
        """

    def tpc_vote(transaction):
        """Promise to commit a transaction

        This is the last chance to fail. A data manager should have
        all changes saved in a recoverable fashion.
        
        Finishes the first phase of a two-phase commit.
        """

    def tpc_finish(transaction):
        """Finish the transaction by permanently saving any tentative changes.

        This *must not fail*.
        """

    def tpc_abort(transaction):
        """Abort (rollback) any tentative commits performed in the transaction
        """

    # XXX subtransaction model is pretty primitive.
    def abort_sub(transaction):
        """Abort any sub-transaction changes"""


    def commit_sub(transaction):
        """Commit (tentatively) subtransaction changes

        This method is called during the first stage of a two-phase commit
        """        
    
