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
$Id: IZopeCursor.py,v 1.3 2002/07/10 23:37:26 srichter Exp $
"""
from IDBICursor import IDBICursor

class IZopeCursor(IDBICursor):
    """An ICursor that integrates with Zope's transactions"""

    def execute(operation, parameters=None):
        """Executes an operation, registering the underlying connection with
        the transaction system.

        See ICursor for more detailed execute information.
        """

    def executemany(operation, seq_of_parameters=None):
        """Executes an operation, registering the underlying connection with
        the transaction system.

        See ICursor for more detailed executemany information.
        """
        
