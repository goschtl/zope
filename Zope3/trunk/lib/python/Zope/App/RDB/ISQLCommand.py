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
$Id: ISQLCommand.py,v 1.1 2002/07/10 23:37:26 srichter Exp $
"""
from Interface import Interface
from Interface.Attribute import Attribute

class ISQLCommand(Interface):
    """Static SQL commands."""
    
    connectionName = Attribute("""The name of the database connection
    to use in getConnection """)

    def getConnection():
        """Get the database connection."""

    def __call__():
        """Execute an sql query and return a result object if appropriate"""

        
__doc__ = ISQLCommand.__doc__






