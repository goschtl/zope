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
$Id: ZopeCursor.py,v 1.2 2002/07/10 23:37:26 srichter Exp $
"""
from types import UnicodeType
from IZopeCursor import IZopeCursor

class ZopeCursor:
    __implements__ = IZopeCursor

    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def execute(self, operation, parameters=None):
        """Executes an operation, registering the underlying
        connection with the transaction system.  """

        if isinstance(operation, UnicodeType):
            operation = operation.encode('UTF-8')
        if parameters is None:
            parameters = {}
        self.connection.registerForTxn()
        return self.cursor.execute(operation, parameters)

    def __getattr__(self, key):
        return getattr(self.cursor, key)
