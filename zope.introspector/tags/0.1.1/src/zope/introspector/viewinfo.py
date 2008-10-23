##############################################################################
#
# Copyright (c) 2007-2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
"""

from zope.interface import Interface, providedBy, alsoProvides
from zope import component
from zope.publisher.browser import BrowserRequest
from zope.publisher.interfaces.browser import (IBrowserSkinType,
                                               IDefaultBrowserLayer)
from zope.introspector.interfaces import IViewInfo
import grokcore.component as grok

class ViewInfo(grok.Adapter):
    """Determine views for contexts.
    """
    grok.implements(IViewInfo)
    grok.context(Interface)
    grok.name('view')
    
    def getViews(self, layer=None):
        request = BrowserRequest(None, {})
        if layer is not None:
            alsoProvides(request, layer)
        sm = component.getSiteManager()
        return sm.adapters.lookupAll(
            (providedBy(self.context), providedBy(request)),
            Interface)
        
    def getAllViews(self):
        for skin_name, layer in getSkins():
            for view_name, factory in self.getViews(layer):
                yield skin_name, layer, view_name, factory
        for view_name, factory in self.getViews(IDefaultBrowserLayer):
            yield u'', IDefaultBrowserLayer, view_name, factory 
            
def getSkins():
    """Get all the skins registered in the system.
    """
    return component.getUtilitiesFor(IBrowserSkinType)

