##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

$Id: Connections.py,v 1.1 2002/12/09 15:26:42 ryzaja Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture import getView

class Connections(BrowserView):

    def update(self):

        conn_names = list(self.context.getAvailableConnections())
        conn_names.sort()

        connections = []
        for conn_name in conn_names:
            registry = self.context.queryConfigurations(conn_name)
            view = getView(registry, "ChangeConfigurations", self.request)
            view.setPrefix(conn_name)
            view.update()
            active = registry.active() is not None
            connections.append(
                {"name": conn_name,
                 "active": active,
                 "inactive": not active,
                 "view": view,
                 })

        return connections
    
