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
$Id: ConnectionService.py,v 1.6 2002/12/09 15:26:42 ryzaja Exp $
"""

from Persistence import Persistent
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.App.ComponentArchitecture.NextService import queryNextService
from Zope.App.OFS.Annotation.IAttributeAnnotatable import IAttributeAnnotatable
from Zope.App.OFS.Services.ConfigurationInterfaces import IConfigurable
from Zope.App.OFS.Services.Configuration import ConfigurationRegistry
from IConnectionManager import IConnectionManager


class ConnectionService(Persistent):

    __doc__ = IConnectionManager.__doc__

    __implements__ = IConnectionManager, IAttributeAnnotatable

    def __init__(self):
        super(ConnectionService, self).__init__()
        self.__bindings = {}    # connectionName -> ConfigurationRegistry


    def getConnection(self, name):
        'See Zope.App.RDB.IConnectionService.IConnectionService'
        registry = self.queryConfigurations(name)
        if registry:
            configuration = registry.active()
            if configuration is not None:
                adapter = configuration.getComponent()
                return adapter()
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
        connections = list(self.__bindings.keys())
        service = queryNextService(self, "SQLDatabaseConnections")
        if service is not None:
            connections.append(service.getAvailableConnections())
        return connections

    getAvailableConnections = ContextMethod(getAvailableConnections)


    def queryConfigurationsFor(self, cfg, default=None):
        'See Zope.App.OFS.Services.ConfigurationInterfaces.IConfigurable'
        return self.queryConfigurations(cfg.connectionName)

    queryConfigurationsFor = ContextMethod(queryConfigurationsFor)

    def queryConfigurations(self, name, default=None):
        registry = self.__bindings.get(name, default)
        return ContextWrapper(registry, self)

    queryConfigurations = ContextMethod(queryConfigurations)

    def createConfigurationsFor(self, cfg):
        'See Zope.App.OFS.Services.ConfigurationInterfaces.IConfigurable'
        return self.createConfigurations(cfg.connectionName)

    createConfigurationsFor = ContextMethod(createConfigurationsFor)

    def createConfigurations(self, name):
        try:
            registry = self.__bindings[name]
        except KeyError:
            self.__bindings[name] = registry = ConfigurationRegistry()
            self._p_changed = 1
        return ContextWrapper(registry, self)
    
    createConfigurations = ContextMethod(createConfigurations)

