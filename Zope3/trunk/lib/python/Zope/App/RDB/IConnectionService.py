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
$Id: IConnectionService.py,v 1.5 2002/12/12 11:32:34 mgedmin Exp $
"""
from Interface import Interface, Attribute

class IConnectionService(Interface):

    def getConnection(name):
        """Returns a connection object by name."""

    def queryConnection(name, default):
        """Returns a connection object by name or default."""

    def getAvailableConnections():
        """Returns the connections available from this connection service."""
