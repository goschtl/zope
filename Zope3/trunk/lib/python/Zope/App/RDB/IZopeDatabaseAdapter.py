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
$Id: IZopeDatabaseAdapter.py,v 1.5 2002/11/08 12:37:13 stevea Exp $
"""
from Zope.App.RDB.IDBITypeInfo import IDBITypeInfo


class IZopeDatabaseAdapter(IDBITypeInfo):
    """Interface for persistent object that returns
    volatile IZopeConnections.

    This object is internal to the connection service."""

    def setDSN(dsn):
        """Set the DSN for the Adapter instance"""

    def getDSN():
        """Get the DSN of the Adapter instance"""

    def connect():
        """Connect to the specified database."""

    def disconnect():
        """Disconnect from the database."""

    def isConnected():
        """Check whether the Zope Connection is actually connected to the
        database."""

    def __call__():
        """Return an IZopeConnection object"""

