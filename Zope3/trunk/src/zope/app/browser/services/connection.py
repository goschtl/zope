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
"""Connection View classes

$Id: connection.py,v 1.16 2003/08/19 13:14:47 srichter Exp $
"""
from zope.app import zapi
from zope.app.component.nextservice import queryNextService
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.services.servicenames import SQLDatabaseConnections, Utilities

class Connections:
    """Connection Overview"""

    def getLocalConnections(self):
        conns = []
        utilities = zapi.getService(self.context, Utilities)
        matching = utilities.getRegisteredMatching(IZopeDatabaseAdapter)
        for match in matching:
            conns.append(self.buildInfo(match))
        return conns


    def getInheritedConnections(self):
        conns = []
        next = queryNextService(self.context, Utilities)
        while next is not None:
            matching = next.getRegisteredMatching(IZopeDatabaseAdapter)
            for match in matching:
                conns.append(self.buildInfo(match))
            next = queryNextService(next, Utilities)
        return conns


    def buildInfo(self, match):
        info = {}
        info['id'] = match[1]
        info['url'] = str(zapi.getView(match[2].active().getComponent(),
                                       'absolute_url', self.request))

        info['dsn'] = match[2].active().getComponent().dsn    
        return info

from zope.app.browser.services.service import ComponentAdding

class ConnectionAdding(ComponentAdding):

    menu_id = "add_connection"

    def add(self, content):
        if not IZopeDatabaseAdapter.isImplementedBy(content):
            raise TypeError("%s is not a zope database adapter" % content)

        return zapi.ContextSuper(ConnectionAdding, self).add(content)
