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

    def prepare(transaction):
        """Begin two-phase commit of a transaction.

        DataManager should return True or False.
        """
        
    def abort(transaction):
        """Abort changes made by transaction."""
    
    def commit(transaction):
        """Commit changes made by transaction."""

    def savepoint(transaction):
        """Do tentative commit of changes to this point.

        Should return an object implementing IRollback
        """
        
class IRollback(Interface):
    
    def rollback():
        """Rollback changes since savepoint."""
