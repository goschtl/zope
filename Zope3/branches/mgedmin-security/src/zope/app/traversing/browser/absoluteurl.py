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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Absolute URL View components

$Id: absoluteurl.py,v 1.2 2004/05/10 06:35:42 philikon Exp $
"""

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.component import getViewProviding, getView
from zope.app.publisher.browser import BrowserView
from zope.app.traversing.browser.interfaces import IAbsoluteURL
from zope.interface import implements
from zope.proxy import sameProxiedObjects
from zope.publisher.browser import IBrowserRequest

_insufficientContext = _("There isn't enough context to get URL information. "
                       "This is probably due to a bug in setting up location "
                       "information.")

def absoluteURL(ob, request):
    return str(getViewProviding(ob, IAbsoluteURL, request))

class AbsoluteURL(BrowserView):
    implements(IAbsoluteURL)

    def __str__(self):
        context = self.context
        request = self.request

        # The application URL contains all the namespaces that are at the
        # beginning of the URL, such as skins, virtual host specifications and
        # so on.
        if sameProxiedObjects(context, request.getVirtualHostRoot()):
            return request.getApplicationURL()

        container = getattr(context, '__parent__', None)
        if container is None:
            raise TypeError, _insufficientContext

        url = str(getView(container, 'absolute_url', request))
        name = getattr(context, '__name__', None)
        if name is None:
            raise TypeError, _insufficientContext

        if name:
            url += '/'+name

        return url

    __call__ = __str__

    def breadcrumbs(self):
        context = self.context
        request = self.request

        # We do this here do maintain the rule that we must be wrapped
        container = getattr(context, '__parent__', None)
        if container is None:
            raise TypeError, _insufficientContext

        if sameProxiedObjects(context, request.getVirtualHostRoot()) or \
               isinstance(context, Exception):
            return ({'name':'', 'url': self.request.getApplicationURL()}, )

        base = tuple(getView(container, 'absolute_url', request).breadcrumbs())

        name = getattr(context, '__name__', None)
        if name is None:
            raise TypeError, _insufficientContext

        if name:
            base += ({'name': name,
                      'url': ("%s/%s" % (base[-1]['url'], name))
                      }, )

        return base

class SiteAbsoluteURL(BrowserView):
    implements(IAbsoluteURL)

    def __str__(self):
        context = self.context
        request = self.request

        if sameProxiedObjects(context, request.getVirtualHostRoot()):
            return request.getApplicationURL()

        url = request.getApplicationURL()
        name = getattr(context, '__name__', None)
        if name:
            url += '/'+name

        return url

    __call__ = __str__

    def breadcrumbs(self):
        context = self.context
        request = self.request

        if sameProxiedObjects(context, request.getVirtualHostRoot()):
            return ({'name':'', 'url': self.request.getApplicationURL()}, )

        base = ({'name':'', 'url': self.request.getApplicationURL()}, )


        name = getattr(context, '__name__', None)
        if name:
            base += ({'name': name,
                      'url': ("%s/%s" % (base[-1]['url'], name))
                      }, )

        return base
