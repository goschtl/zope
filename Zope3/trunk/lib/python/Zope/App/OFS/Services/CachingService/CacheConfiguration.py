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
"""A configuration for a cache.

$Id: CacheConfiguration.py,v 1.3 2002/12/21 15:32:54 poster Exp $
"""

from ICacheConfiguration import ICacheConfiguration
from Zope.App.OFS.Services.Configuration import NamedComponentConfiguration
from Zope.App.OFS.Services.Configuration import ConfigurationStatusProperty
from Zope.ComponentArchitecture import getService
from Zope.App.Event.IObjectEvent import IObjectModifiedEvent
from Zope.ContextWrapper import ContextMethod

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
