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
"""Local/persistent surrogate (adapter) registry support

$Id: surrogate.py,v 1.5 2004/03/08 17:26:55 jim Exp $
"""

from persistent import Persistent
from persistent.dict import PersistentDict
from zope.interface.adapter import Surrogate, AdapterRegistry
from zope.interface.adapter import adapterImplied, Default
from zope.app.services.registration import NotifyingRegistrationStack
import zope.app.component.nextservice
import zope.app.container.contained
import zope.app.interfaces.services.service
import zope.app.interfaces.services.registration
from zope.app import zapi

class LocalSurrogate(Surrogate):
    """Local surrogates

    Local surrogates are transient, rather than persistent.

    Their adapter data are stored in their registry objects.
    """

    def __init__(self, spec, registry):
        Surrogate.__init__(self, spec, registry)
        self.registry = registry
        registry.baseFor(spec).subscribe(self)

    def clean(self):
        spec = self.spec()
        base = self.registry.baseFor(spec)
        ladapters = self.registry.adapters.get(spec)
        if ladapters:
            adapters = base.adapters.copy()
            adapters.update(ladapters)
        else:
            adapters = base.adapters
        self.adapters = adapters
        Surrogate.clean(self)

class LocalSurrogateRegistry(AdapterRegistry, Persistent):
    """Local/persistent surrogate registry
    """

    zope.interface.implements(
        zope.app.interfaces.services.registration.IRegistry,
        )
    
    _surrogateClass = LocalSurrogate
    next = None
    subs = ()

    def __init__(self, base, next=None):
        self.base = base
        self.adapters = {}
        self.stacks = PersistentDict()
        AdapterRegistry.__init__(self)
        self.setNext(next)

    def setNext(self, next, base=None):
        if base is not None:
            self.base = base
        if self.next is not None:
            self.next.removeSub(self)
        if next is not None:
            next.addSub(self)
        self.next = next
        self.adaptersChanged()

    def addSub(self, sub):
        self.subs += (sub, )

    def removeSub(self, sub):
        self.subs = tuple([s for s in self.subs if s is not sub])

    def __getstate__(self):
        state = Persistent.__getstate__(self).copy()
        del state['_surrogates']
        del state['_default']
        del state['_remove']
        return state

    def __setstate__(self, state):
        Persistent.__setstate__(self, state)
        AdapterRegistry.__init__(self)
    
    def baseFor(self, spec):
        return self.base.get(spec)

    def queryRegistrationsFor(self, registration, default=None):
        stacks = self.stacks.get(registration.required)
        if stacks:
            stack = stacks.get((False, registration.with, registration.name,
                                registration.provided))
            if stack is not None:
                return stack

        return default

    _stackType = NotifyingRegistrationStack

    def createRegistrationsFor(self, registration):
        stacks = self.stacks.get(registration.required)
        if stacks is None:
            stacks = PersistentDict()
            self.stacks[registration.required] = stacks

        key = False, registration.with, registration.name, registration.provided
        stack = stacks.get(key)
        if stack is None:
            stack = self._stackType(self)
            stacks[key] = stack

        return stack

    def adaptersChanged(self, *args):

        adapters = {}
        if self.next is not None:
            for required, radapters in self.next.adapters.iteritems():
                adapters[required] = radapters.copy()
        
        for required, stacks in self.stacks.iteritems():
            if required is None:
                required = Default
            radapters = adapters.get(required)
            if not radapters:
                radapters = {}
                adapters[required] = radapters

            for key, stack in stacks.iteritems():
                registration = stack.active()
                if registration is not None:
                    radapters[key] = registration.factories


        if adapters != self.adapters:
            self.adapters = adapters
            for surrogate in self._surrogates.values():
                surrogate.dirty()
            for sub in self.subs:
                sub.adaptersChanged()

    notifyActivated = notifyDeactivated = adaptersChanged

class LocalSurrogateBasedService(
    zope.app.container.contained.Contained,
    Persistent,
    ):
    """A service that uses local surrogate registries

    A local surrogate-based service needs to maintain connections
    between it's surrogate registries and those of containing ans
    sub-services.

    The service must implement a setNext method that will be called
    with the next local service, which may be None, and the global
    service. This method will be called when a service is bound.
    
    """

    zope.interface.implements(
        zope.app.interfaces.services.service.IBindingAware,
        )

    def __updateNext(self, servicename):
        next = zope.app.component.nextservice.getNextService(self, servicename)
        global_ = zapi.getService(None, servicename)
        if next == global_:
            next = None
        self.setNext(next, global_)
        
    def bound(self, servicename):
        self.__updateNext(servicename)
        
        # Now, we need to notify any sub-site services. This is
        # a bit complicated because our immediate subsites might not have
        # the same service. Sigh
        sm = zapi.getServiceManager(self)
        self.__notifySubs(sm.subSites, servicename)

    def unbound(self, servicename):
        sm = zapi.getServiceManager(self)
        self.__notifySubs(sm.subSites, servicename)

    def __notifySubs(self, subs, servicename):
        for sub in subs:
            s = sub.queryLocalService(servicename)
            if s is not None:
                s.__updateNext(servicename)
            else:
                self.__notifySubs(sub.subSites, servicename)
