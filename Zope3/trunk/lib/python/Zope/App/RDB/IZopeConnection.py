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
$Id: IZopeConnection.py,v 1.1 2002/06/24 11:14:17 srichter Exp $
"""

from IDBIConnection import IDBIConnection
from IDBITypeInfoProvider import IDBITypeInfoProvider
from Transactions.IDataManager import IDataManager

class IZopeConnection(IDBIConnection, IDataManager, IDBITypeInfoProvider):

    def cursor():
        """
        return a ZopeCursor object
        """
    

        
