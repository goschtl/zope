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
$Id: IZopeConnection.py,v 1.4 2002/07/24 23:17:04 jeremy Exp $
"""

from IDBIConnection import IDBIConnection
from IDBITypeInfoProvider import IDBITypeInfoProvider

class IZopeConnection(IDBIConnection, IDBITypeInfoProvider):

    # XXX What does the next paragraph mean?
    
    # An implementation of this object will be exposed to the
    # user. Therefore the Zope connection represents a connection in
    # the Zope sense, meaning that the object might not be actually
    # connected to a database.

    def cursor():
        """Return an IZopeCursor object."""
        
    def registerForTxn():
        """Join the current transaction.

        This method should only be inovoked by the Zope/DB transaction
        manager.
        """
