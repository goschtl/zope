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

$Id: CachingService.py,v 1.2 2002/12/06 11:01:11 alga Exp $
"""
from types import TupleType

from Zope.App.ComponentArchitecture.NextService import queryNextService
from Zope.ContextWrapper import ContextMethod

from Zope.App.OFS.Container.IContainer import IHomogenousContainer, IContainer
from Zope.App.OFS.Container.BTreeContainer import BTreeContainer

from Zope.Event.IEventChannel import IEventChannel
from Zope.Event.EventChannel import EventChannel

from Zope.App.Caching.ICachingService import ICachingService
from Zope.App.Caching.ICache import ICache


class ILocalCachingService(ICachingService, IContainer,
                           IHomogenousContainer,
                           IEventChannel):
    """TTW manageable caching service"""


class CachingService(BTreeContainer, EventChannel):

    __implements__ = ILocalCachingService

    def __init__(self):
        BTreeContainer.__init__(self)
        EventChannel.__init__(self)

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
