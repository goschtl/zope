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

$Id: CachingService.py,v 1.8 2002/12/18 20:23:04 stevea Exp $
"""
__metaclass__ = type

from Persistence import Persistent
from Zope.App.Caching.ICachingService import ICachingService
from Zope.App.ComponentArchitecture.NextService import queryNextService
from Zope.App.OFS.Services.ConfigurationInterfaces \
        import INameComponentConfigurable
from Zope.App.OFS.Services.Configuration import NameComponentConfigurable
from Zope.App.OFS.Services.LocalEventService.ProtoServiceEventChannel \
        import ProtoServiceEventChannel
from Zope.ContextWrapper import ContextMethod
from Zope.Event.IEventChannel import IEventChannel
from Zope.Event.IObjectEvent import IObjectModifiedEvent


class ILocalCachingService(ICachingService, IEventChannel,
                           INameComponentConfigurable):
    """TTW manageable caching service"""


class CachingService(ProtoServiceEventChannel, NameComponentConfigurable):

    __implements__ = (ILocalCachingService,
                      ProtoServiceEventChannel.__implements__)

    _subscribeToServiceInterface = IObjectModifiedEvent

    def __init__(self):
        # XXX If we know that all the superclasses do the right thing in
        #     __init__ with respect to calling
        #     super(ClassName, self).__init__(*args, **kw), then we can
        #     replace the following with just a call to super.
        Persistent.__init__(self)
        ProtoServiceEventChannel.__init__(self)
        NameComponentConfigurable.__init__(self)

    def getCache(wrapped_self, name):
        'See Zope.App.Caching.ICachingService.ICachingService'
        cache = wrapped_self.queryActiveComponent(name)
        if cache:
            return cache
        service = queryNextService(wrapped_self, "Caching")
        if service is not None:
            return service.getCache(name)
        raise KeyError, name
    getCache = ContextMethod(getCache)

    def queryCache(wrapped_self, name, default=None):
        'See Zope.App.Caching.ICachingService.ICachingService' 
        try:
            return wrapped_self.getCache(name)
        except KeyError:
            return default
    queryCache = ContextMethod(queryCache)

    def getAvailableCaches(wrapped_self):
        'See Zope.App.Caching.ICachingService.ICachingService'
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

