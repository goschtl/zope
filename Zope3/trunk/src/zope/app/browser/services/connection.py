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

$Id: connection.py,v 1.21 2004/03/02 13:48:25 philikon Exp $
"""
from zope.app import zapi
from zope.app.browser.services.service import ComponentAdding
from zope.app.component.nextservice import queryNextService
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.rdb.interfaces import IZopeDatabaseAdapter
from zope.app.services.servicenames import Utilities

class Connections:
    """Connection Overview"""

    def getLocalConnections(self):
        conns = []
        utilities = zapi.getService(self.context, Utilities)
        for id, conn in utilities.getLocalUtilitiesFor(IZopeDatabaseAdapter):
            conns.append(self.buildInfo(id, conn))
        return conns

    def getInheritedConnections(self):
        conns = []
        utilities = queryNextService(self.context, Utilities)
        for id, conn in utilities.getUtilitiesFor(IZopeDatabaseAdapter):
            conns.append(self.buildInfo(id, conn))
        return conns

    def buildInfo(self, id, conn):
        info = {}
        info['id'] = id
        info['url'] = str(zapi.getView(conn, 'absolute_url', self.request))
        info['dsn'] = conn.dsn
        return info


class ConnectionAdding(ComponentAdding):

    menu_id = "add_connection"

    def add(self, content):
        if not IZopeDatabaseAdapter.isImplementedBy(content):
            error = _("${object} is not a Zope database adapter.")
            error.mapping['object'] = str(content)

        return super(ConnectionAdding, self).add(content)
