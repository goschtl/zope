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

$Id: cache.py,v 1.18 2004/03/05 22:08:55 jim Exp $
"""
from zope.app import zapi
from zope.app.browser.services.service import ComponentAdding
from zope.app.component.nextservice import queryNextService
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.cache.interfaces import ICache
from zope.app.services.servicenames import Utilities

class Caches:
    """View for local caching services."""

    def getLocalCaches(self):
        caches = []
        utilities = zapi.getService(self.context, Utilities)
        for id, cache in utilities.getLocalUtilitiesFor(ICache):
            caches.append(self.buildInfo(id, cache))
        return caches

    def getInheritedCaches(self):
        caches = []
        utilities = queryNextService(self.context, Utilities)
        for id, cache in utilities.getUtilitiesFor(ICache):
            caches.append(self.buildInfo(id, cache))
        return caches

    def buildInfo(self, id, cache):
        info = {}
        info['id'] = id
        info['url'] = str(zapi.getView(cache, 'absolute_url', self.request))
        return info


class CacheAdding(ComponentAdding):

    menu_id = "add_cache"

    def add(self, content):
        if not ICache.providedBy(content):
            error = _("${object} is not a Cache.")
            error.mapping['object'] = str(content)
            raise TypeError(error)

        return super(CacheAdding, self).add(content)
