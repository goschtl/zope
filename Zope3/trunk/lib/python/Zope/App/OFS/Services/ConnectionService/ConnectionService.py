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
"""$Id: ConnectionService.py,v 1.1 2002/06/24 16:18:50 srichter Exp $
"""

from Zope.ComponentArchitecture import getNextService
from IConnectionManager import IConnectionManager
from Persistence import PersistentMapping, Persistent

class ConnectionService(Persistent):
    
    __implements__ = IConnectionManager

    def __init__(self):
        self.__connections = PersistentMapping()

    # IContainer methods
    def __getitem__(self, key):
        """see interface Zope.App.OFS.Container.IContainer."""
        return self.__connections[key]

    def get(self, key, default=None):
        """see interface Zope.App.OFS.Container.IContainer."""        
        return self.__connections.get(key, default)

    def __contains__(self, key):
        """see interface Zope.App.OFS.Container.IContainer."""        
        return self.__connections.has_key(key)

    def keys(self):
        """see interface Zope.App.OFS.Container.IContainer."""        
        return self.__connections.keys()

    def values(self):
        """see interface Zope.App.OFS.Container.IContainer."""        
        return self.__connections.values()

    def items(self):
        """see interface Zope.App.OFS.Container.IContainer."""        
        return self.__connections.items()

    def __len__(self):
        """see interface Zope.App.OFS.Container.IContainer."""        
        return len(self.__connections)

    def setObject(self, key, object):
        """see interface Zope.App.OFS.Container.IContainer."""        
        self.__connections[key] = object
        return object

    def __delitem__(self, key):
        """see interface Zope.App.OFS.Container.IContainer."""        
        del self.__connections[key]

    # IConnectionService methods
    def getConnection(self, name):
        """see interface Zope.App.RDB.IConnectionService """
        return self[name]()
        
    def queryConnection(self, name, default):
        """see interface Zope.App.RDB.IConnectionService """        
        return self.get(name, default)()

    def getAvailableConnections(self):
        """Returns the connections known to this connection service"""
        # XXX, not yet
        # connections = self.keys()
        # return connections + \getNextService(self, "ConnectionService").getAvailableConnections()
    
