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

$Id: cache.py,v 1.3 2002/12/30 14:03:16 stevea Exp $
"""
__metaclass__ = type

from persistence import Persistent
from zope.app.interfaces.cache.cache import ICachingService
from zope.app.component.nextservice import queryNextService
from zope.app.interfaces.services.configuration \
        import INameComponentConfigurable
from zope.app.services.configuration import NameComponentConfigurable
from zope.app.services.event import ServiceSubscriberEventChannel
from zope.proxy.context import ContextMethod
from zope.app.interfaces.services.event import IEventChannel
from zope.app.interfaces.event import IObjectModifiedEvent


class ILocalCachingService(ICachingService, IEventChannel,
                           INameComponentConfigurable):
    """TTW manageable caching service"""


class CachingService(ServiceSubscriberEventChannel, NameComponentConfigurable):

    __implements__ = (ILocalCachingService,
                      ServiceSubscriberEventChannel.__implements__)

    _subscribeToServiceInterface = IObjectModifiedEvent

    def __init__(self):
        # XXX If we know that all the superclasses do the right thing in
        #     __init__ with respect to calling
        #     super(ClassName, self).__init__(*args, **kw), then we can
        #     replace the following with just a call to super.
        Persistent.__init__(self)
        ServiceSubscriberEventChannel.__init__(self)
        NameComponentConfigurable.__init__(self)

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
        for name in wrapped_self.listConfigurationNames():
            registry = wrapped_self.queryConfigurations(name)
            if registry.active() is not None:
                caches[name] = 0
        service = queryNextService(wrapped_self, "Caching")
        if service is not None:
            for name in service.getAvailableCaches():
                caches[name] = 0
        return caches.keys()
    getAvailableCaches = ContextMethod(getAvailableCaches)



"""A configuration for a cache.

$Id: cache.py,v 1.3 2002/12/30 14:03:16 stevea Exp $
"""

from zope.app.interfaces.services.cache import ICacheConfiguration
from zope.app.services.configuration import NamedComponentConfiguration
from zope.app.services.configuration import ConfigurationStatusProperty
from zope.component import getService
from zope.app.interfaces.event import IObjectModifiedEvent
from zope.proxy.context import ContextMethod

class CacheConfiguration(NamedComponentConfiguration):

    __doc__ = ICacheConfiguration.__doc__

    __implements__ = (ICacheConfiguration,
                      NamedComponentConfiguration.__implements__)

    status = ConfigurationStatusProperty('Caching')

    label = "Cache"

    def __init__(self, *args, **kw):
        super(CacheConfiguration, self).__init__(*args, **kw)

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
