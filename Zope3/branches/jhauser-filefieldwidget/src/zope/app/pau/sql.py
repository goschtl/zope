##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""SQL Authentication Plugin.

$Id: sql.py,v 1.0 2004/10/11 mriya3
"""
from zope.app.sqlscript import SQLScript
import zope.interface
import interfaces

class SQLAuthenticationPlugin(SQLScript):
    """ SQL Authentication Plugin for Pluggable Authentication System """
    
    zope.interface.implements(interfaces.IAuthenticationPlugin)
        
    def authenticateCredentials(self, credentials):
        result = self(**credentials)
        if not len(result):
            return None
        return str(result[0]['id']),result[0]


        
        
