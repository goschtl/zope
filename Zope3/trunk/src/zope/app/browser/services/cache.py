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
"""Cache registry support classes.

$Id: cache.py,v 1.13 2003/08/19 17:34:02 srichter Exp $
"""
from zope.app import zapi
from zope.app.browser.services.service import ComponentAdding
from zope.app.component.nextservice import queryNextService
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.cache import ICache
from zope.app.services.servicenames import Caching, Utilities

class Caches:
    """View for local caching services."""

    def getLocalCaches(self):
        caches = []
        utilities = zapi.getService(self.context, Utilities)
        matching = utilities.getRegisteredMatching(ICache)
        for match in matching:
            caches.append(self.buildInfo(match))
        return caches


    def getInheritedCaches(self):
        caches = []
        next = queryNextService(self.context, Utilities)
        while next is not None:
            matching = next.getRegisteredMatching(ICache)
            for match in matching:
                caches.append(self.buildInfo(match))
            next = queryNextService(next, Utilities)
        return caches


    def buildInfo(self, match):
        info = {}
        info['id'] = match[1]
        info['url'] = str(zapi.getView(match[2].active().getComponent(),
                                       'absolute_url', self.request))

        return info


class CacheAdding(ComponentAdding):

    menu_id = "add_cache"

    def add(self, content):
        if not ICache.isImplementedBy(content):
            raise TypeError("%s is not a Cache" % content)

        return zapi.ContextSuper(CacheAdding, self).add(content)
