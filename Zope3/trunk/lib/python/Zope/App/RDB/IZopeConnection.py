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

Revision information:
$Id: IZopeConnection.py,v 1.2 2002/06/25 15:41:45 k_vertigo Exp $
"""

from IDBIConnection import IDBIConnection
from IDBITypeInfoProvider import IDBITypeInfoProvider


class IZopeConnection(IDBIConnection,  IDBITypeInfoProvider):

    def cursor():
        """Return an IZopeCursor object"""
        
    def registerForTxn():
        """Registers the Connection with the Zope Transaction
        framework.

        This method should only be inovoked by the Zope/DB transaction
        manager."""

    def unregisterFromTxn():
        """Unregister the connection from the Zope transaction.

        This method should only be inovoked by the Zope/DB transaction
        manager!!!."""


        


