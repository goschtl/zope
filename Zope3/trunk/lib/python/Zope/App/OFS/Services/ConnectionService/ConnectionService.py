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
$Id: ConnectionService.py,v 1.2 2002/07/10 23:52:18 srichter Exp $
"""
from types import TupleType

from Zope.ComponentArchitecture import queryNextService
from Zope.ContextWrapper import ContextMethod

from Zope.App.OFS.Container.IContainer import IHomogenousContainer, IContainer
from Zope.App.OFS.Container.BTreeContainer import BTreeContainer

from Zope.App.RDB.IConnectionService import IConnectionService
from Zope.App.RDB.IZopeDatabaseAdapter import IZopeDatabaseAdapter

class ILocalConnectionService(IConnectionService, IContainer,
                              IHomogenousContainer):
    """TTW manageable connection service"""
    

class ConnectionService(BTreeContainer):

    __implements__ =  ILocalConnectionService

    ############################################################
    # Implementation methods for interface
    # Zope.App.RDB.ConnectionService.ILocalConnectionService

    ######################################
    # from: Zope.App.RDB.IConnectionService.IConnectionService

    def getConnection(self, name):
        'See Zope.App.RDB.IConnectionService.IConnectionService'
        return self.__getitem__(name)()

    def queryConnection(self, name, default=None):
        'See Zope.App.RDB.IConnectionService.IConnectionService' 
        adapter = self.get(name, default)
        if adapter is not default:
            return adapter()
        return default

    def getAvailableConnections(self):
        'See Zope.App.RDB.IConnectionService.IConnectionService'
        connections = list(self.keys())
        service = queryNextService(self, "ConnectionService")
        if service is not None:
            connections.append(service.getAvailableConnections())
        return connections

    getAvailableConnections = ContextMethod(getAvailableConnections)

    ######################################
    # from: Zope.App.OFS.Container.IContainer.IHomogenousContainer

    def isAddable(self, interfaces):
        'See Zope.App.OFS.Container.IContainer.IHomogenousContainer'
        if type(interfaces) != TupleType:
            interfaces = (interfaces,)
        if IZopeDatabaseAdapter in interfaces:
            return 1
        return 0

    #
    ############################################################
