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
$Id: ConnectionService.py,v 1.7 2002/12/12 11:32:31 mgedmin Exp $
"""

from Persistence import Persistent
from Zope.ContextWrapper import ContextMethod
from Zope.App.ComponentArchitecture.NextService import queryNextService
from Zope.App.OFS.Services.ConfigurationInterfaces import INameConfigurable
from Zope.App.OFS.Services.Configuration import NameConfigurable
from Zope.App.RDB.IConnectionService import IConnectionService


class ILocalConnectionService(IConnectionService, INameConfigurable):
    """A local (placeful) connection service"""


class ConnectionService(Persistent, NameConfigurable):

    __doc__ = ILocalConnectionService.__doc__

    __implements__ = ILocalConnectionService

    def __init__(self):
        super(ConnectionService, self).__init__()
        NameConfigurable.__init__(self)


    def getConnection(self, name):
        'See Zope.App.RDB.IConnectionService.IConnectionService'
        registry = self.queryConfigurations(name)
        if registry:
            configuration = registry.active()
            if configuration is not None:
                adapter = configuration.getComponent()
                return adapter()
        service = queryNextService(self, "SQLDatabaseConnections")
        if service is not None:
            return service.getConnection(name)
        raise KeyError, name

    getConnection = ContextMethod(getConnection)

    def queryConnection(self, name, default=None):
        'See Zope.App.RDB.IConnectionService.IConnectionService'
        try:
            return self.getConnection(name)
        except KeyError:
            return default

    queryConnection = ContextMethod(queryConnection)

    def getAvailableConnections(self):
        'See Zope.App.RDB.IConnectionService.IConnectionService'
        connections = {}
        for name in self.listConfigurationNames():
            registry = self.queryConfigurations(name)
            if registry.active() is not None:
                connections[name] = 0
        service = queryNextService(self, "SQLDatabaseConnections")
        if service is not None:
            for name in service.getAvailableConnections():
                connections[name] = 0
        return connections.keys()

    getAvailableConnections = ContextMethod(getAvailableConnections)

