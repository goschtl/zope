##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Browser view for the LocalInterfaceService."""

from zope.interface.interfaces import IMethod
from zope.schema.interfaces import IField
from zope.app.interfaces.services.interface import IInterfaceBasedRegistry

from zope.app import zapi

class Interfaces:

    def getInterfaces(self):
        L = [(iface.__name__, id) for id, iface in self.context.items()]
        L.sort()
        return [{"id": id, "name": name} for name, id in L]

class Detail:

    def setup(self):
        id = self.request["id"]
        iface = self.context.getInterface(id)

        from zope.proxy import getProxiedObject
        self.iface = getProxiedObject(iface)
        
        self.name = self.iface.__name__
        # XXX the doc string needs some formatting for presentation
        # XXX self.doc = self.iface.__doc__
        self.doc = self.iface.getDoc()
        self.methods = []
        self.schema = []

        for name in self.iface:
            defn = self.iface[name]
            if IMethod.isImplementedBy(defn):
                self.methods.append(defn)
            elif IField.isImplementedBy(defn):
                self.schema.append(defn)

    def getServices(self):
        """Return an iterable of service dicts

        where the service dicts contains keys "name" and "registrations."
        registrations is a list of IRegistrations.
        """
        sm = zapi.getServiceManager(self.context)
        for name, iface in sm.getServiceDefinitions():
            service = sm.queryService(name)
            if service is None:
                continue
            registry = zapi.queryAdapter(service, IInterfaceBasedRegistry)
            if registry is None:
                continue
            regs = list(registry.getRegistrationsForInterface(self.iface))
            if regs:
                yield {"name": name, "registrations": regs}
            
