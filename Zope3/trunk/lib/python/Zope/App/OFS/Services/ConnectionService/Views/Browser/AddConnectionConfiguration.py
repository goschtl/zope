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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: AddConnectionConfiguration.py,v 1.2 2002/12/09 16:32:58 ryzaja Exp $
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

    def action(self, component_path):
        connection_name = self.connectionName.getData()
        cd = ConnectionConfiguration(connection_name, component_path)
        cd = self.context.add(cd)
        getWidgetsDataForContent(self, IConnectionConfiguration, content=cd,
                                 required=True)
        self.request.response.redirect(self.context.nextURL())
