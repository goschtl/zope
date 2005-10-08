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
from zope.app.apidoc.utilities import getFunctionSignature

class XMLRPCIntrospection(object):

    def listAllMethods(self):
        """ lists all methods available """
        return self._getXMLRPCMethods()

    def methodHelp(self, method_name):
        pass

    def methodSignature(self, method_name):
        """ returns the method signature """
        return self._getXMLRPCMethodSignature(method_name)

    def __call__(self, *args, **kw):
        return self.listAllMethods()

    #
    # Introspection APIS
    #
    _reserved_method_names = (u'', u'listAllMethods', u'methodHelp',
                              u'methodSignature')

    def _filterXMLRPCRequestRegistrations(self, registrations):
        """ XXX might be outsourced in some utility """
        for registration in registrations:
            for required_iface in registration.required:
                if (required_iface is IXMLRPCRequest and
                    registration.name.strip() not in
                    self._reserved_method_names):
                    yield registration

    def _getRegistrationAdapters(self, interfaces):
        """ XXX might be outsourced in some utility """
        results = []
        for interface in interfaces:
            registrations = list(getViews(interface, IXMLRPCRequest))
            filtered_adapters = list(self._filterXMLRPCRequestRegistrations(registrations))
            results.extend(filtered_adapters)
        return results

    #
    # Lookup APIS
    #
    def _getXMLRPCMethods(self):
        adapter_registrations = []
        interfaces = list(providedBy(self.context))

        for result in self._getRegistrationAdapters(interfaces):
            if result.name not in adapter_registrations:
                adapter_registrations.append(result.name)

        adapter_registrations.sort()
        return adapter_registrations

    def _getFunctionAttributesDoc(self, function):
        return getFunctionSignature(function)

    def _getXMLRPCMethodSignature(self, method_name):
        interfaces = list(providedBy(self.context))

        for result in self._getRegistrationAdapters(interfaces):
            if result.name == method_name:
                method = getattr(result.value, method_name)
                return self._getFunctionAttributesDoc(method)
        # XXX see RFC here, if we want to raise or no
        return None

