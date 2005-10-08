##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""XML-RPC Introspection mechanism

$Id:$
"""
__docformat__ = 'restructuredtext'

from zope.interface import providedBy
from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest
from zope.app.publisher.xmlrpc import XMLRPCView
from zope.app.apidoc.presentation import getViews, filterViewRegistrations,\
                                         SPECIFIC_INTERFACE_LEVEL

class XMLRPCIntrospection(XMLRPCView):

    def _getXMLRPCViews(self):
        adapter_registrations = []
        interfaces = list(providedBy(self.context))

        for interface in interfaces:
            registrations = list(getView(interface, IXMLRPCRequest))
            results = filterViewRegistrations(registrations,IXMLRPCRequest,
                                              level=SPECIFIC_INTERFACE_LEVEL)
            adapter_registrations.append(list(results))

        return adapter_registrations

    def listAllMethods(self):
        return []

    def methodHelp(self, method_name):
        pass

    def methodSignature(self, method_name):
        pass

