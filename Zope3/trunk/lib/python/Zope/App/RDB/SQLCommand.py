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
$Id: SQLCommand.py,v 1.1 2002/07/10 23:37:26 srichter Exp $
"""
from Zope.ComponentArchitecture import getNextService

from ISQLCommand import ISQLCommand
from Util import queryForResults


class SQLCommand:
    """A simple version of a SQL Command."""

    __implements__ = ISQLCommand

    def __init__(self, connection_name='', sql=''):
        self.connectionName = connection_name
        self.sql = sql

    ############################################################
    # Implementation methods for interface
    # Zope.App.RDB.ISQLCommand.

    def getConnection(self):
        'See Zope.App.RDB.ISQLCommand.ISQLCommand'
        connection_service = getNextService(self, "ConnectionService")
        connection = connection_service.getConnection(self.connectionName)
        return connection

    def __call__(self):
        return queryForResults(self.getConnection(), self.sql)

    #
    ############################################################
