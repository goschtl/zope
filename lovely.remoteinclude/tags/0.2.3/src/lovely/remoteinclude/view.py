##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
$Id$
"""
__docformat__ = 'restructuredtext'

from zope.publisher.browser import BrowserPage
from zope.publisher.browser import BrowserView
from zope.cachedescriptors.property import Lazy
from zope.traversing.browser import absoluteURL
from lovely.responsecache.interfaces import IResponseCacheSettings
from zope import component
from zope import interface
from zope.app.component.hooks import getSite
import interfaces
from zope.contentprovider.interfaces import BeforeUpdateEvent
from zope import event

def includeView(context, request):
    return component.queryMultiAdapter((context, request),
                                       name='include')

class IncludeableView(object):

    """base class for registering via page directive"""
    interface.implements(interfaces.IIncludeableView)

    def update(self):
        pass

    def render(self):
        return self.index()

    def __call__(self):
        event.notify(BeforeUpdateEvent(self, self.request))
        self.update()
        return self.render()

class IncludeView(BrowserPage):

    @Lazy
    def viewURL(self):
        cs = component.queryMultiAdapter(
            (self.context, self.request), IResponseCacheSettings)
        if cs is not None:
            return cs.key
        # we return the path from site if we have no key
        siteURL = absoluteURL(getSite(), self.request)
        cURL = absoluteURL(self.context, self.request)
        return cURL[len(siteURL):]

    def __call__(self):
        s = """<!--# include virtual="%s" -->"""
        return s % self.viewURL

    def browserDefault(self, request):
        return (self, ())
