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
"""
$Id: interfaces.py,v 1.2 2004/03/18 14:31:49 philikon Exp $
"""

from zope.interface import Interface

class IUndoManager(Interface):
    """Interface for the Undo Manager"""

    def getUndoInfo(first=0, last=-20, user_name=None):
        """
        Gets some undo information. It skips the 'first' most
        recent transactions; i.e. if first is N, then the first
        transaction returned will be the Nth transaction.

        If last is less than zero, then its absolute value is the
        maximum number of transactions to return.  Otherwise if last
        is N, then only the N most recent transactions following start
        are considered.

        If user_name is not None, only transactions from the given
        user_name are returned.

        Note: at the moment, doesnt care where called from

        returns sequence of mapping objects by date desc

        keys of mapping objects:
          id          -> internal id for zodb
          user_name   -> name of user that last accessed the file
          time        -> unix timestamp of last access
          datetime    -> datetime object of time
          description -> transaction description
        """

    def undoTransaction(id_list):
        """
        id_list will be a list of transaction ids.
        iterate over each id in list, and undo
        the transaction item.
        """
