##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""Local utility service implementation.

Besides being functional, this module also serves as an example of
creating a local service; see README.txt.

$Id$
"""

from zope.app.adapter.adapter import LocalAdapterService
from zope.app import zapi
from zope.app.registration.registration import ComponentRegistration
from zope.app.utility.interfaces import ILocalUtilityService
from zope.app.utility.interfaces import IUtilityRegistration
from zope.component.utility import UtilityService
from zope.security.proxy import removeSecurityProxy
import zope.app.site.interfaces
import zope.interface
import zope.interface.adapter

class LocalUtilityService(UtilityService, LocalAdapterService):
    """Local Utility Service
    """

    serviceType = zapi.servicenames.Utilities

    zope.interface.implementsOnly(
        ILocalUtilityService,
        zope.app.site.interfaces.ISimpleService,
        zope.app.site.interfaces.IBindingAware,
        )


    def queryRegistrations(self, name, interface):
        return self.queryRegistrationsFor(
            UtilityRegistration(name, interface, None)
            )

    def getLocalUtilitiesFor(self, interface):
        # This method is deprecated and is temporarily provided for
        # backward compatability
        from zope.app import zapi
        from zope.app.component.localservice import getNextService
        next = getNextService(self, zapi.servicenames.Utilities)
        next_utils = dict(next.getUtilitiesFor(interface))
        for name, util in self.getUtilitiesFor(interface):
            if next_utils.get(name) != util:
                yield name, util


    def _updateAdaptersFromLocalData(self, adapters):
        LocalAdapterService._updateAdaptersFromLocalData(self, adapters)
        
        for required, stacks in self.stacks.iteritems():
            if required is None:
                required = Default
            radapters = adapters.get(required)

            for key, stack in stacks.iteritems():
                registration = stack.active()
                if registration is not None:
                    key = True, key[1], '', key[3]

                    # Needs more thought:
                    # We have to remove the proxy because we're
                    # storing the value amd we can't store proxies.
                    # (Why can't we?)  we need to think more about
                    # why/if this is truly safe
                    
                    radapters[key] = radapters.get(key, ()) + (
                        removeSecurityProxy(registration.factory), )



class UtilityRegistration(ComponentRegistration):
    """Utility component registration for persistent components

    This registration configures persistent components in packages to
    be utilities.
    """

    serviceType = zapi.servicenames.Utilities

    ############################################################
    # To make adapter code happy. Are we going too far?
    #
    required = zope.interface.adapter.Null
    with = ()
    provided = property(lambda self: self.interface)
    factory = property(lambda self: self.getComponent())
    #
    ############################################################

    zope.interface.implements(IUtilityRegistration)


    component = property(lambda self: self.getComponent())

    def __init__(self, name, interface, component_path, permission=None):
        ComponentRegistration.__init__(self, component_path, permission)
        self.name = name
        self.interface = interface

    def usageSummary(self):
        # Override IRegistration.usageSummary()
        component = self.getComponent()
        s = self.getInterface().getName()
        if self.name:
            s += " registered as '%s'" % self.name
        s += ", implemented by %s" %component.__class__.__name__
        s += " '%s'"%self.componentPath
        return s

    def getInterface(self):
        # ComponentRegistration calls this when you specify a
        # permission; it needs the interface to create a security
        # proxy for the interface with the given permission.
        return self.interface
