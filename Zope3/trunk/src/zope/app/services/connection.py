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

$Id: connection.py,v 1.16 2003/06/23 00:31:31 jim Exp $
"""

from persistence import Persistent
from zope.app.component.nextservice import queryNextService
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.interfaces.services.connection import IConnectionRegistration
from zope.app.interfaces.services.connection import ILocalConnectionService
from zope.app.interfaces.services.service import ISimpleService
from zope.app.services.registration import NameComponentRegistry
from zope.app.services.registration import NamedComponentRegistration
from zope.context import ContextMethod
from zope.interface import implements

class ConnectionService(Persistent, NameComponentRegistry):

    __doc__ = ILocalConnectionService.__doc__

    implements(ILocalConnectionService, ISimpleService)

    def getConnection(self, name):
        'See IConnectionService'
        dbadapter = self.queryActiveComponent(name)
        if dbadapter is not None:
            return dbadapter()
        service = queryNextService(self, "SQLDatabaseConnections")
        if service is not None:
            return service.getConnection(name)
        raise KeyError, name

    getConnection = ContextMethod(getConnection)

    def queryConnection(self, name, default=None):
        'See IConnectionService'
        try:
            return self.getConnection(name)
        except KeyError:
            return default

    queryConnection = ContextMethod(queryConnection)

    def getAvailableConnections(self):
        'See IConnectionService'
        connections = {}
        for name in self.listRegistrationNames():
            registry = self.queryRegistrations(name)
            if registry.active() is not None:
                connections[name] = 0
        service = queryNextService(self, "SQLDatabaseConnections")
        if service is not None:
            # Note that this works because we're only interested in the names
            # of connections. If we wanted other data about connections, we'd
            # have to be careful not to override this service's connections
            # with higher-up connections.
            for name in service.getAvailableConnections():
                connections[name] = 0
        return connections.keys()

    getAvailableConnections = ContextMethod(getAvailableConnections)


class ConnectionRegistration(NamedComponentRegistration):

    __doc__ = IConnectionRegistration.__doc__

    implements(IConnectionRegistration)

    serviceType = 'SQLDatabaseConnections'

    label = "Connection"

    def getInterface(self):
        return IZopeDatabaseAdapter


# XXX Pickle backward compatability
ConnectionConfiguration = ConnectionRegistration
