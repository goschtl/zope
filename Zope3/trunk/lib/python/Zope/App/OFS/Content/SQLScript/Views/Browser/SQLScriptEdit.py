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
$Id: SQLScriptEdit.py,v 1.1 2002/07/11 00:03:18 srichter Exp $
"""
from Zope.ComponentArchitecture import getNextService
from Zope.App.Traversing import getParent

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.Content.SQLScript.ISQLScript import ISQLScript

class SQLScriptEdit(BrowserView):
    """Edit View for SQL Scripts"""
    __implements__ = BrowserView.__implements__
    __used_for__ = ISQLScript

    def edit(self, connection, arguments, sql):
        if arguments != self.context.getArgumentsString():
            self.context.setArguments(arguments)
        if sql != self.context.getSource():
            self.context.setSource(sql)
        if connection != self.context.getConnectionName():
            self.context.setConnectionName(connection)
        return self.request.response.redirect(self.request['nextURL'])


    def getAllConnections(self):
        parent = getParent(self.context)
        connection_service = getNextService(parent, "ConnectionService")
        connections = connection_service.getAvailableConnections()
        return connections
