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

$Id: CacheableView.py,v 1.1 2002/10/09 13:08:44 alga Exp $
"""

from Zope.App.Caching.ICacheable import ICacheable
from Zope.App.OFS.Annotation.IAnnotatable import IAnnotatable
from Zope.App.Caching.Caching import getCacheForObj
from Zope.App.PageTemplate import ViewPageTemplateFile
#from Zope.App.Forms.Views.Browser.FormView import FormView
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.Forms.Widget import CustomWidget
from Zope.App.Forms.Views.Browser import Widget
from Zope.ComponentArchitecture import getService, getAdapter
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Schema.Exceptions import StopValidation, ValidationError, \
     ValidationErrorsAll, ConversionErrorsAll
from Zope.App.Forms.Exceptions import WidgetInputError

class CacheableView(BrowserView):

    __used_for__ = IAnnotatable
    
    form = ViewPageTemplateFile("edit.pt")

    def invalidate(self):
        "Invalidate the current cached value."

        cache = getCacheForObj(self.context)
        if cache:
            cache.invalidate(self.context)
            return self.form(message="Invalidated.")
        else:
            return self.form(message="No cache associated with object.")

    def action(self):
        "Change the cacheId"
        try:
            cacheId = self._getCacheIdWidget().getData()
        except (ValidationErrorsAll, ConversionErrorsAll), e:
            return self.form(errors=e)
        except WidgetInputError, e:
            #return self.form(errors=e.errors)
            return repr(e.errors)
        else:
            getAdapter(self.context, ICacheable).setCacheId(cacheId)
            return self.form(message="Saved changes.")

    def renderCacheId(self):
        cacheId = getAdapter(self.context, ICacheable).getCacheId()
        return self._getCacheIdWidget().render(cacheId)
    
    def _getCacheIdWidget(self):
        cacheId = getAdapter(self.context, ICacheable).getCacheId()
        field = ICacheable.getDescriptionFor('cacheId')
        field = ContextWrapper(field, self.context)
        w = CustomWidget(Widget.ListWidget, size=1)
        return w(field, self.request)




