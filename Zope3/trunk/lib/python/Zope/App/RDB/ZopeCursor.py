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
$Id: ZopeCursor.py,v 1.1 2002/06/25 15:41:45 k_vertigo Exp $
"""
from IZopeCursor import IZopeCursor

class ZopeCursor:
    __implements__ = IZopeCursor

    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def execute(self, operation, parameters=None):
        """Executes an operation, registering the underlying
        connection with the transaction system.  """

        self.connection.registerForTxn()
        return self.cursor.execute(operation, parameters)

    def __getattr__(self, key):
        return getattr(self.cursor, key)
