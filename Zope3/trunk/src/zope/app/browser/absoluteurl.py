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

$Id: absoluteurl.py,v 1.13 2003/08/28 22:40:24 sidnei Exp $
"""

from zope.app import zapi
from zope.publisher.browser import BrowserView
from zope.proxy import sameProxiedObjects

from zope.app.i18n import ZopeMessageIDFactory as _

_insufficientContext = _("There isn't enough context to get URL information. "
                       "This is probably due to a bug in setting up context "
                       "wrappers.")


class AbsoluteURL(BrowserView):

    def __str__(self):
        context = self.context
        request = self.request

        # We do this here do maintain the rule that we must be wrapped
        container = zapi.getWrapperContainer(context)
        if container is None:
            raise TypeError, _insufficientContext

        if sameProxiedObjects(context, request.getVirtualHostRoot()):
            return request.getApplicationURL()

        url = str(zapi.getView(container, 'absolute_url', request))

        dict = zapi.getInnerWrapperData(context)
        try:
            name = dict['name']
        except KeyError:
            raise TypeError, _insufficientContext

        if name:
            url += '/'+name

        return url

    __call__ = __str__

    def breadcrumbs(self):
        context = self.context
        request = self.request

        # We do this here do maintain the rule that we must be wrapped
        container = zapi.getWrapperContainer(context)
        if container is None:
            raise TypeError, _insufficientContext

        if sameProxiedObjects(context, request.getVirtualHostRoot()):
            return ({'name':'', 'url': self.request.getApplicationURL()}, )

        base = zapi.getView(container, 'absolute_url', request).breadcrumbs()

        dict = zapi.getInnerWrapperData(context)
        try:
            name = dict['name']
        except KeyError:
            raise TypeError, _insufficientContext

        if name:
            base += ({'name': name,
                      'url': ("%s/%s" % (base[-1]['url'], name))
                      }, )

        return base

class SiteAbsoluteURL(BrowserView):

    def __str__(self):
        context = self.context
        request = self.request

        if sameProxiedObjects(context, request.getVirtualHostRoot()):
            return request.getApplicationURL()

        url = request.getApplicationURL()

        dict = zapi.getInnerWrapperData(context)
        if dict:
            name = dict.get('name')
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


        dict = zapi.getInnerWrapperData(context)
        if dict:
            name = dict.get('name')

            if name:
                base += ({'name': name,
                          'url': ("%s/%s" % (base[-1]['url'], name))
                          }, )


        return base
