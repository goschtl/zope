##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Service Details View

$Id: browser.py,v 1.1 2004/01/29 17:51:17 srichter Exp $
"""
from zope.app import zapi
from zope.app.location import LocationProxy
from zope.interface.declarations import providedBy
from zope.products.apidoc.ifacemodule.browser import InterfaceDetails
from zope.products.apidoc.utilities import getPythonPath
from zope.proxy import removeAllProxies
from zope.schema.interfaces import IField


class Menu(object):
    """Menu View Helper Class"""

    def getMenuTitle(self, node):
        """Return the title of the node that is displayed in the menu."""
        return zapi.name(node.context)

    def getMenuLink(self, node):
        """Return the HTML link of the node that is displayed in the menu."""
        return './'+ zapi.name(node.context) + '/index.html'


class ServiceDetails(object):
    """View for a Service in the API Documentation"""

    def interface(self):
        """Get the details view of the interface the service provides."""
        iface = LocationProxy(self.context.interface,
                               self.context,
                               getPythonPath(self.context.interface))
        return InterfaceDetails(iface, self.request)
    
    def implementations(self):
        """Retrieve a list of implementations of this service."""
        impl = map(removeAllProxies, self.context.implementations)
        impl = map(lambda x: x.__class__, self.context.implementations)
        return map(getPythonPath, impl)
