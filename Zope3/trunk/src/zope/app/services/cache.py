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

$Id: cache.py,v 1.17 2003/08/19 17:34:24 srichter Exp $
"""
from persistence import Persistent
from zope.app import zapi
from zope.app.component.nextservice import queryNextService
from zope.app.interfaces.cache import ICache
from zope.app.interfaces.event import IObjectModifiedEvent
from zope.app.interfaces.services.cache import ILocalCachingService
from zope.app.interfaces.services.service import ISimpleService
from zope.app.services.event import ServiceSubscriberEventChannel
from zope.app.services.servicenames import Caching, Utilities
from zope.component import getService
from zope.context import ContextMethod
from zope.interface import implements

class CachingService(ServiceSubscriberEventChannel, Persistent):

    implements(ILocalCachingService, ISimpleService)

    _subscribeToServiceInterface = IObjectModifiedEvent

    def __init__(self):
        super(CachingService, self).__init__()

    def getCache(self, name):
        'See ICachingService'
        utilities = zapi.getService(self, Utilities)
        matching = utilities.getRegisteredMatching(ICache)
        matching = filter(lambda m: m[1] == name, matching)
        if matching and matching[0][2].active() is not None:
            return matching[0][2].active().getComponent()
        service = queryNextService(self, Caching)
        if service is not None:
            return service.getCache(name)
        raise KeyError, name
    getCache = ContextMethod(getCache)

    def queryCache(self, name, default=None):
        'See ICachingService'
        try:
            return self.getCache(name)
        except KeyError:
            return default
    queryCache = ContextMethod(queryCache)

    def getAvailableCaches(self):
        'See ICachingService'
        caches = []
        utilities = zapi.getService(self, Utilities)
        matching = utilities.getRegisteredMatching(ICache)
        for match in matching:
            if match[2].active() is not None:
                caches.append(match[1])
        service = queryNextService(self, Caching)
        if service is not None:
            for name in service.getAvailableCaches():
                if name not in caches:
                    caches.append(name)
        return caches
    getAvailableCaches = ContextMethod(getAvailableCaches)
