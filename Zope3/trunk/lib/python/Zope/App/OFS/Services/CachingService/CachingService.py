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

$Id: CachingService.py,v 1.3 2002/12/06 18:03:31 alga Exp $
"""
from types import TupleType
from Zope.App.Caching.ICache import ICache
from Zope.App.Caching.ICachingService import ICachingService
from Zope.App.ComponentArchitecture.NextService import queryNextService
from Zope.App.OFS.Container.BTreeContainer import BTreeContainer
from Zope.App.OFS.Container.IContainer import IHomogenousContainer, IContainer
from Zope.App.OFS.Services.LocalEventService.ProtoServiceEventChannel \
     import ProtoServiceEventChannel
from Zope.ContextWrapper import ContextMethod
from Zope.Event.EventChannel import EventChannel
from Zope.Event.IEventChannel import IEventChannel
from Zope.Event.IObjectEvent import IObjectModifiedEvent


class ILocalCachingService(ICachingService, IContainer,
                           IHomogenousContainer,
                           IEventChannel):
    """TTW manageable caching service"""


class CachingService(BTreeContainer, ProtoServiceEventChannel):

    __implements__ = ILocalCachingService, ProtoServiceEventChannel.__implements__

    _subscribeToServiceInterface = IObjectModifiedEvent

    def __init__(self):
        BTreeContainer.__init__(self)
        ProtoServiceEventChannel.__init__(self)

    def __nonzero__(self):
        # XXX otherwise 'if service:' in getService() fails when len(service) == 0
        return 1

    def getCache(self, name):
        'See Zope.App.Caching.ICachingService.ICachingService'
        return self.__getitem__(name)

    def queryCache(self, name, default=None):
        'See Zope.App.Caching.ICachingService.ICachingService' 
        cache = self.get(name, default)
        if cache is not default:
            return cache
        return default

    def getAvailableCaches(self):
        'See Zope.App.Caching.ICachingService.ICachingService'
        caches = list(self.keys())
        service = queryNextService(self, "Caching")
        if service is not None:
            caches.append(service.getAvailableCaches())
        return caches
    getAvailableCaches = ContextMethod(getAvailableCaches)

    def isAddable(self, interfaces):
        'See Zope.App.OFS.Container.IContainer.IHomogenousContainer'
        if type(interfaces) != TupleType:
            interfaces = (interfaces,)
        if ICache in interfaces:
            return 1
        return 0

    def setObject(self, key, object):
        "See Zope.App.OFS.Container.IContainer.IWriteContainer"
        self.subscribe(object, IObjectModifiedEvent)
        BTreeContainer.setObject(self, key, object)

    def __delitem__(self, key):
        "See Zope.App.OFS.Container.IContainer.IWriteContainer"
        self.unsubscribe(self[key], IObjectModifiedEvent)
        BTreeContainer.__delitem__(self, key)
