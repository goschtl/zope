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

$Id: CachingService.py,v 1.4 2002/12/12 15:28:16 mgedmin Exp $
"""
from Persistence import Persistent
from Zope.App.Caching.ICachingService import ICachingService
from Zope.App.ComponentArchitecture.NextService import queryNextService
from Zope.App.OFS.Services.ConfigurationInterfaces import INameConfigurable
from Zope.App.OFS.Services.Configuration import NameConfigurable
from Zope.App.OFS.Services.LocalEventService.ProtoServiceEventChannel \
     import ProtoServiceEventChannel
from Zope.ContextWrapper import ContextMethod
from Zope.Event.IEventChannel import IEventChannel
from Zope.Event.IObjectEvent import IObjectModifiedEvent


class ILocalCachingService(ICachingService, IEventChannel, INameConfigurable):
    """TTW manageable caching service"""


class CachingService(Persistent, ProtoServiceEventChannel, NameConfigurable):

    __implements__ = ILocalCachingService, ProtoServiceEventChannel.__implements__

    _subscribeToServiceInterface = IObjectModifiedEvent

    def __init__(self):
        Persistent.__init__(self)
        ProtoServiceEventChannel.__init__(self)
        NameConfigurable.__init__(self)

    def getCache(self, name):
        'See Zope.App.Caching.ICachingService.ICachingService'
        cache = self.queryActiveComponent(name)
        if cache:
            return cache
        service = queryNextService(self, "Caching")
        if service is not None:
            return service.getCache(name)
        raise KeyError, name

    getCache = ContextMethod(getCache)

    def queryCache(self, name, default=None):
        'See Zope.App.Caching.ICachingService.ICachingService' 
        try:
            return self.getCache(name)
        except KeyError:
            return default

    queryCache = ContextMethod(queryCache)

    def getAvailableCaches(self):
        'See Zope.App.Caching.ICachingService.ICachingService'
        caches = {}
        for name in self.listConfigurationNames():
            registry = self.queryConfigurations(name)
            if registry.active() is not None:
                caches[name] = 0
        service = queryNextService(self, "Caching")
        if service is not None:
            for name in service.getAvailableCaches():
                caches[name] = 0
        return caches.keys()

    getAvailableCaches = ContextMethod(getAvailableCaches)

