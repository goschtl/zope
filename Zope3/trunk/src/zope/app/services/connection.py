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

$Id: connection.py,v 1.21 2003/09/21 17:31:59 jim Exp $
"""
from persistence import Persistent
from zope.app import zapi
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.interfaces.services.connection import ILocalConnectionService
from zope.app.interfaces.services.service import ISimpleService
from zope.app.services.servicenames import Utilities
from zope.interface import implements
from zope.app.container.contained import Contained

class ConnectionService(Persistent, Contained):
    """This is a local relational database connection service."""

    implements(ILocalConnectionService, ISimpleService)

    def getConnection(self, name):
        'See IConnectionService'
        utilities = zapi.getService(self, Utilities)
        dbadapter = utilities.getUtility(IZopeDatabaseAdapter, name)
        return dbadapter()

    def queryConnection(self, name, default=None):
        'See IConnectionService'
        utilities = zapi.getService(self, Utilities)
        dbadapter = utilities.queryUtility(IZopeDatabaseAdapter, None, name)
        if dbadapter:
            return dbadapter()
        else:
            return default

    def getAvailableConnections(self):
        'See IConnectionService'
        utilities = zapi.getService(self, Utilities)
        connections = utilities.getUtilitiesFor(IZopeDatabaseAdapter)
        return map(lambda c: c[0], connections)
