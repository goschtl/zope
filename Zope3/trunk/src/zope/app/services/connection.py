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
$Id: connection.py,v 1.2 2002/12/25 14:13:19 jim Exp $
"""

from persistence import Persistent
from zope.proxy.context import ContextMethod
from zope.app.component.nextservice import queryNextService
from zope.app.interfaces.services.configuration \
        import INameComponentConfigurable
from zope.app.services.configuration import NameComponentConfigurable
from zope.app.interfaces.rdb import IConnectionService


class ILocalConnectionService(IConnectionService, INameComponentConfigurable):
    """A local (placeful) connection service"""


class ConnectionService(Persistent, NameComponentConfigurable):

    __doc__ = ILocalConnectionService.__doc__

    __implements__ = ILocalConnectionService

    def __init__(self):
        super(ConnectionService, self).__init__()

    def getConnection(self, name):
        'See IConnectionService'
        adapter = self.queryActiveComponent(name)
        if adapter is not None:
            return adapter()
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



"""A configuration for a database adapter.

$Id: connection.py,v 1.2 2002/12/25 14:13:19 jim Exp $
"""

from zope.app.interfaces.services.connection import IConnectionConfiguration
from zope.app.services.configuration import NamedComponentConfiguration
from zope.app.services.configuration import ConfigurationStatusProperty

class ConnectionConfiguration(NamedComponentConfiguration):

    __doc__ = IConnectionConfiguration.__doc__

    __implements__ = (IConnectionConfiguration,
                      NamedComponentConfiguration.__implements__)

    status = ConfigurationStatusProperty('SQLDatabaseConnections')

    label = "Connection"

    def __init__(self, *args, **kw):
        super(ConnectionConfiguration, self).__init__(*args, **kw)
