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

$Id: cache.py,v 1.21 2004/03/01 10:57:39 philikon Exp $
"""
from persistent import Persistent
from zope.interface import implements

from zope.app import zapi
from zope.app.interfaces.event import IObjectModifiedEvent
from zope.app.interfaces.services.cache import ILocalCachingService
from zope.app.interfaces.services.service import ISimpleService
from zope.app.cache.interfaces import ICache
from zope.app.services.event import ServiceSubscriberEventChannel
from zope.app.services.servicenames import Utilities
from zope.app.container.contained import Contained

class CachingService(ServiceSubscriberEventChannel, Persistent, Contained):

    implements(ILocalCachingService, ISimpleService)

    _subscribeToServiceInterface = IObjectModifiedEvent

    def __init__(self):
        super(CachingService, self).__init__()

    def getCache(self, name):
        'See ICachingService'
        utilities = zapi.getService(self, Utilities)
        return utilities.getUtility(ICache, name)
    

    def queryCache(self, name, default=None):
        'See ICachingService'
        utilities = zapi.getService(self, Utilities)
        return utilities.queryUtility(ICache, default, name)
    

    def getAvailableCaches(self):
        'See ICachingService'
        utilities = zapi.getService(self, Utilities)
        caches = utilities.getUtilitiesFor(ICache)
        return map(lambda c: c[0], caches)
    
