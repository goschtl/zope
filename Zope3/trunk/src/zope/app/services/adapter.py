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
"""Adapter Service

$Id: adapter.py,v 1.24 2004/02/20 16:57:30 fdrake Exp $
"""
__metaclass__ = type

from zope.app import zapi
import sys
import zope.app.component.interfacefield
import zope.app.interfaces.services.registration
import zope.app.interfaces.services.service
import zope.app.security.permission
import zope.app.services.registration
import zope.app.services.surrogate
import zope.component.interfaces
import zope.interface
import zope.schema


class LocalAdapterService(
    zope.app.services.surrogate.LocalSurrogateRegistry,
    zope.app.services.surrogate.LocalSurrogateBasedService,
    ):

    zope.interface.implements(
        zope.component.interfaces.IAdapterService,
        zope.app.interfaces.services.service.ISimpleService,
        )

    def __init__(self):
        zope.app.services.surrogate.LocalSurrogateRegistry.__init__(
            self, zapi.getService(None, zapi.servicenames.Adapters)
            )

        

class IAdapterRegistration(
    zope.app.interfaces.services.registration.IRegistration):

    required = zope.app.component.interfacefield.InterfaceField(
        title = u"For interface",
        description = u"The interface of the objects being adapted",
        readonly = True,
        basetype = None,
        )

    provided = zope.app.component.interfacefield.InterfaceField(
        title = u"Provided interface",
        description = u"The interface provided",
        readonly = True,
        required = True,
        )

    name = zope.schema.TextLine(
        title=u"Name",
        readonly=True,
        required=False,
        )

    factoryName = zope.schema.BytesLine(
        title=u"The dotted name of a factory for creating the adapter",
        readonly = True,
        required = True,
        )

    permission = zope.app.security.permission.PermissionField(
        title=u"The permission required for use",
        readonly=False,
        required=False,
        )
        
    factories = zope.interface.Attribute(
        "A sequence of factories to be called to construct the component"
        )

class AdapterRegistration(zope.app.services.registration.SimpleRegistration):

    zope.interface.implements(IAdapterRegistration)

    serviceType = zapi.servicenames.Adapters

    with = () # XXX Don't support multi-adapters yet

    # XXX These should be positional arguments, except that required
    #     isn't passed in if it is omitted. To fix this, we need a
    #     required=False,explicitly_unrequired=True in the schema field
    #     so None will get passed in.
    def __init__(self, provided, factoryName,
                 name='', required=None, permission=None):
        self.required = required
        self.provided = provided
        self.name = name
        self.factoryName = factoryName
        self.permission = permission

    def factories(self):
        folder = self.__parent__.__parent__
        factory = folder.resolve(self.factoryName)
        return factory,
    factories = property(factories)

# XXX Pickle backward compatability
AdapterConfiguration = AdapterRegistration


#BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB

import persistent
from zope.interface.surrogate import ReadProperty

AdapterRegistration.required = ReadProperty(lambda self: self.forInterface)
AdapterRegistration.provided = ReadProperty(
    lambda self: self.providedInterface)
AdapterRegistration.name     = ReadProperty(lambda self: self.adapterName)

class AdapterService(persistent.Persistent):
    pass
