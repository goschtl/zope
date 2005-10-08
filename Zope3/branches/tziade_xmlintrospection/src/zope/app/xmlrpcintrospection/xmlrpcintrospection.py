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
from zope.app.apidoc.presentation import getViews, filterViewRegistrations

class XMLRPCIntrospection(object):

    _reserved_method_names = (u'', u'listAllMethods', u'methodHelp',
                              u'methodSignature')

    def _filterXMLRPCRequestRegistrations(self, registrations):
        for registration in registrations:
            for required_iface in registration.required:
                if (required_iface is IXMLRPCRequest and
                    registration.name.strip() not in
                    self._reserved_method_names):
                    yield registration.name

    def _getXMLRPCMethods(self):
        adapter_registrations = []
        interfaces = list(providedBy(self.context))

        for interface in interfaces:
            registrations = list(getViews(interface, IXMLRPCRequest))
            results = list(self._filterXMLRPCRequestRegistrations(registrations))
            for result in results:
                if result not in adapter_registrations:
                    adapter_registrations.append(result)

        adapter_registrations.sort()
        return adapter_registrations

    def listAllMethods(self):
        return self._getXMLRPCMethods()

    def methodHelp(self, method_name):
        pass

    def methodSignature(self, method_name):
        pass

    def __call__(self, *args, **kw):
        return self.listAllMethods()

