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
"""Connection service

$Id: connection.py,v 1.18 2003/08/19 07:09:53 srichter Exp $
"""
from persistence import Persistent
from zope.app import zapi
from zope.app.component.nextservice import queryNextService
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.interfaces.services.connection import ILocalConnectionService
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.services.service import ISimpleService
from zope.app.services.servicenames import SQLDatabaseConnections, Utilities
from zope.interface import implements

class ConnectionService(Persistent):
    """This is a local relational database connection service."""

    implements(ILocalConnectionService, ISimpleService)

    def getConnection(self, name):
        'See IConnectionService'
        utilities = zapi.getService(self, Utilities)
        matching = utilities.getRegisteredMatching(IZopeDatabaseAdapter)
        matching = filter(lambda m: m[1] == name, matching)
        if matching and matching[0][2].active() is not None:
            return matching[0][2].active().getComponent()
        service = queryNextService(self, SQLDatabaseConnections)
        if service is not None:
            return service.getConnection(name)
        raise KeyError, name

    getConnection = zapi.ContextMethod(getConnection)

    def queryConnection(self, name, default=None):
        'See IConnectionService'
        try:
            return self.getConnection(name)
        except KeyError:
            return default

    queryConnection = zapi.ContextMethod(queryConnection)

    def getAvailableConnections(self):
        'See IConnectionService'
        connections = []
        utilities = zapi.getService(self, Utilities)
        matching = utilities.getRegisteredMatching(IZopeDatabaseAdapter)
        for match in matching:
            if match[2].active() is not None:
                connections.append(match[1])
        service = queryNextService(self, SQLDatabaseConnections)
        if service is not None:
            for name in service.getAvailableConnections():
                if name not in connections:
                    connections.append(name)
        return connections

    getAvailableConnections = zapi.ContextMethod(getAvailableConnections)
