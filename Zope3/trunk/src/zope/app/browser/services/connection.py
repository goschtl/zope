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

$Id: connection.py,v 1.2 2002/12/25 14:12:36 jim Exp $
"""
__metaclass__ = type

from zope.component import getServiceManager
from zope.publisher.browser import BrowserView
from zope.app.form.utility import setUpWidgets, getWidgetsDataForContent
from zope.app.interfaces.services.connection \
     import IConnectionConfiguration
from zope.app.services.connection \
     import ConnectionConfiguration
from zope.app.interfaces.rdb import IZopeDatabaseAdapter

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

    def action(self, connection_name, component_path=None):
        if not connection_name:
            raise ValueError('You must specify a connection name')
        if not component_path:
            raise ValueError('You must specify a component path')
        cd = ConnectionConfiguration(connection_name, component_path)
        cd = self.context.add(cd)
        getWidgetsDataForContent(self, IConnectionConfiguration, content=cd)
        self.request.response.redirect(self.context.nextURL())
