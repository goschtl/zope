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

$Id: cache.py,v 1.18 2003/08/19 23:11:05 srichter Exp $
"""
from persistence import Persistent
from zope.app import zapi
from zope.app.interfaces.cache import ICache
from zope.app.interfaces.event import IObjectModifiedEvent
from zope.app.interfaces.services.cache import ILocalCachingService
from zope.app.interfaces.services.service import ISimpleService
from zope.app.services.event import ServiceSubscriberEventChannel
from zope.app.services.servicenames import Utilities
from zope.interface import implements

class CachingService(ServiceSubscriberEventChannel, Persistent):

    implements(ILocalCachingService, ISimpleService)

    _subscribeToServiceInterface = IObjectModifiedEvent

    def __init__(self):
        super(CachingService, self).__init__()

    def getCache(self, name):
        'See ICachingService'
        utilities = zapi.getService(self, Utilities)
        return utilities.getUtility(ICache, name)
    getCache = zapi.ContextMethod(getCache)

    def queryCache(self, name, default=None):
        'See ICachingService'
        utilities = zapi.getService(self, Utilities)
        return utilities.queryUtility(ICache, default, name)
    queryCache = zapi.ContextMethod(queryCache)

    def getAvailableCaches(self):
        'See ICachingService'
        utilities = zapi.getService(self, Utilities)
        caches = utilities.getUtilitiesFor(ICache)
        return map(lambda c: c[0], caches)
    getAvailableCaches = zapi.ContextMethod(getAvailableCaches)
