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
"""Connection configuration adding view

$Id: AddConnectionConfiguration.py,v 1.3 2002/12/12 11:32:31 mgedmin Exp $
"""
__metaclass__ = type

from Zope.ComponentArchitecture import getServiceManager
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.Forms.Utility import setUpWidgets, getWidgetsDataForContent
from Zope.App.OFS.Services.ConnectionService.IConnectionConfiguration \
     import IConnectionConfiguration
from Zope.App.OFS.Services.ConnectionService.ConnectionConfiguration \
     import ConnectionConfiguration
from Zope.App.RDB.IZopeDatabaseAdapter import IZopeDatabaseAdapter

class AddConnectionConfiguration(BrowserView):

    def __init__(self, *args):
        super(AddConnectionConfiguration, self).__init__(*args)
        setUpWidgets(self, IConnectionConfiguration)

    def components(self):
        service = getServiceManager(self.context.context)
        paths = [info['path']
                 for info in service.queryComponent(type=IZopeDatabaseAdapter)]
        paths.sort()
        return paths

    def action(self, connection_name, component_path):
        if not connection_name:
            raise ValueError, 'You must specify a connection name'
        cd = ConnectionConfiguration(connection_name, component_path)
        cd = self.context.add(cd)
        getWidgetsDataForContent(self, IConnectionConfiguration, content=cd)
        self.request.response.redirect(self.context.nextURL())
