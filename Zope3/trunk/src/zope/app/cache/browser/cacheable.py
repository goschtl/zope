##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Management view for binding caches to content objects.

$Id: cacheable.py,v 1.2 2004/03/06 16:50:17 jim Exp $
"""
from zope.app import zapi
from zope.app.cache.caching import getCacheForObj, getLocationForCache
from zope.app.form.utility import setUpEditWidgets
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.annotation import IAnnotatable
from zope.app.cache.interfaces import ICacheable
from zope.app.interfaces.form import WidgetInputError
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView

class CacheableView(BrowserView):

    __used_for__ = IAnnotatable

    form = ViewPageTemplateFile("cacheableedit.pt")

    def __init__(self, *args):
        super(CacheableView, self).__init__(*args)
        self.cacheable = ICacheable(self.context)
        setUpEditWidgets(self, ICacheable, self.cacheable)

    def current_cache_id(self):
        "Returns the current cache ID."
        return self.cacheable.getCacheId()

    def current_cache_url(self):
        "Returns the current cache provider's URL."
        # XXX: it would be *really* useful to the user to be able to jump to
        # the cache component and see the stats etc. directly from the
        # cacheable view.  All this needs is to find out the URL somehow.
        return None

    def invalidate(self):
        "Invalidate the current cached value."

        cache = getCacheForObj(self.context)
        location = getLocationForCache(self.context)
        if cache and location:
            cache.invalidate(location)
            return self.form(message=_("cache-invalidated", u"Invalidated."))
        else:
            return self.form(message=_("no-cache-associated",
                                       u"No cache associated with object."))

    def action(self):
        "Change the cacheId"
        try:
            cacheId = self.cacheId.getData()
        except WidgetInputError, e:
            #return self.form(errors=e.errors)
            return repr(e.errors)
        else:
            self.cacheable.setCacheId(cacheId)
            return self.form(message=_(u"Saved changes."))
