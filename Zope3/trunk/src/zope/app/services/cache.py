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
"""Caching service.

$Id: cache.py,v 1.16 2003/06/23 00:31:31 jim Exp $
"""

from persistence import Persistent
from zope.app.component.nextservice import queryNextService
from zope.app.interfaces.cache.cache import ICache, ICachingService
from zope.app.interfaces.event import IObjectModifiedEvent
from zope.app.interfaces.services.cache import ICacheRegistration
from zope.app.interfaces.services.registration import INameComponentRegistry
from zope.app.interfaces.services.event import IEventChannel
from zope.app.interfaces.services.service import ISimpleService
from zope.app.services.registration import NameComponentRegistry
from zope.app.services.registration import NamedComponentRegistration
from zope.app.services.event import ServiceSubscriberEventChannel
from zope.component import getService
from zope.context import ContextMethod
from zope.interface import implements

class ILocalCachingService(ICachingService, IEventChannel,
                           INameComponentRegistry):
    """TTW manageable caching service"""


class CachingService(ServiceSubscriberEventChannel, NameComponentRegistry):

    implements(ILocalCachingService, ISimpleService)

    _subscribeToServiceInterface = IObjectModifiedEvent

    def __init__(self):
        # XXX If we know that all the superclasses do the right thing in
        #     __init__ with respect to calling
        #     super(ClassName, self).__init__(*args, **kw), then we can
        #     replace the following with just a call to super.
        # XXX Disagree.  __init__ doesn't always have the same signature,
        #     hence cllaborative super doesn't apply to __init__, at least
        #     not in general.  (It may work by convention for Fields.)
        #     --Guido
        Persistent.__init__(self)
        ServiceSubscriberEventChannel.__init__(self)
        NameComponentRegistry.__init__(self)

    def getCache(wrapped_self, name):
        'See ICachingService'
        cache = wrapped_self.queryActiveComponent(name)
        if cache:
            return cache
        service = queryNextService(wrapped_self, "Caching")
        if service is not None:
            return service.getCache(name)
        raise KeyError, name
    getCache = ContextMethod(getCache)

    def queryCache(wrapped_self, name, default=None):
        'See ICachingService'
        try:
            return wrapped_self.getCache(name)
        except KeyError:
            return default
    queryCache = ContextMethod(queryCache)

    def getAvailableCaches(wrapped_self):
        'See ICachingService'
        caches = {}
        for name in wrapped_self.listRegistrationNames():
            registry = wrapped_self.queryRegistrations(name)
            if registry.active() is not None:
                caches[name] = 0
        service = queryNextService(wrapped_self, "Caching")
        if service is not None:
            for name in service.getAvailableCaches():
                caches[name] = 0
        return caches.keys()
    getAvailableCaches = ContextMethod(getAvailableCaches)


class CacheRegistration(NamedComponentRegistration):

    __doc__ = ICacheRegistration.__doc__

    implements(ICacheRegistration)

    serviceType = 'Caching'

    label = "Cache"

    def activated(wrapped_self):
        cache = wrapped_self.getComponent()
        service = getService(wrapped_self, 'Caching')
        service.subscribe(cache, IObjectModifiedEvent)
    activated = ContextMethod(activated)

    def deactivated(wrapped_self):
        cache = wrapped_self.getComponent()
        service = getService(wrapped_self, 'Caching')
        service.unsubscribe(cache, IObjectModifiedEvent)
        cache.invalidateAll()
    deactivated = ContextMethod(deactivated)

    def getInterface(self):
        return ICache


# XXX Pickle backward compatability
CacheConfiguration = CacheRegistration
