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

$Id: cacheable.py,v 1.2 2002/12/25 14:12:28 jim Exp $
"""

from zope.component import getService, getAdapter
from zope.proxy.context import ContextWrapper
from zope.publisher.browser import BrowserView
from zope.schema.interfaces import StopValidation, ValidationError, \
     ValidationErrorsAll, ConversionErrorsAll

from zope.app.browser.form.widget import Widget
from zope.app.cache.caching import getCacheForObj, getLocationForCache
from zope.app.form.utility import setUpEditWidgets
from zope.app.form.widget import CustomWidget
from zope.app.interfaces.annotation import IAnnotatable
from zope.app.interfaces.cache.cache import ICacheable
from zope.app.interfaces.forms import WidgetInputError
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class CacheableView(BrowserView):

    __used_for__ = IAnnotatable

    form = ViewPageTemplateFile("edit.pt")

    def __init__(self, *args):
        super(CacheableView, self).__init__(*args)
        self.cachable = getAdapter(self.context, ICacheable)
        setUpEditWidgets(self, ICacheable, self.cachable)

    def invalidate(self):
        "Invalidate the current cached value."

        cache = getCacheForObj(self.context)
        location = getLocationForCache(self.context)
        if cache and location:
            cache.invalidate(location)
            return self.form(message="Invalidated.")
        else:
            return self.form(message="No cache associated with object.")

    def action(self):
        "Change the cacheId"
        try:
            cacheId = self.cacheId.getData()
        except (ValidationErrorsAll, ConversionErrorsAll), e:
            return self.form(errors=e)
        except WidgetInputError, e:
            #return self.form(errors=e.errors)
            return repr(e.errors)
        else:
            self.cachable.setCacheId(cacheId)
            return self.form(message="Saved changes.")
