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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: IZopeCursor.py,v 1.1 2002/06/24 11:14:17 srichter Exp $
"""

from IDBICursor import IDBICursor

class IZopeCursor(IDBICursor):

    """an iCursor that integrates with zope's transactions"""

    def execute(operation, parameters=None):
        """executes an operation, registering the underlying connection with
        the transaction system.

        See ICursor for more detailed execute information.
        """

    def executemany(operation, seq_of_parameters=None):
        """executes an operation, registering the underlying connection with
        the transaction system.

        See ICursor for more detailed executemany information.
        """
        
