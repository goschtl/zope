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

$Id: CacheableView.py,v 1.3 2002/12/03 08:55:53 ryzaja Exp $
"""

from Zope.App.Caching.ICacheable import ICacheable
from Zope.App.OFS.Annotation.IAnnotatable import IAnnotatable
from Zope.App.Caching.Caching import getCacheForObj, getLocationForCache
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.Forms.Widget import CustomWidget
from Zope.App.Forms.Views.Browser import Widget
from Zope.ComponentArchitecture import getService, getAdapter
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Schema.Exceptions import StopValidation, ValidationError, \
     ValidationErrorsAll, ConversionErrorsAll
from Zope.App.Forms.Exceptions import WidgetInputError
from Zope.App.Forms.Utility import setUpEditWidgets

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




