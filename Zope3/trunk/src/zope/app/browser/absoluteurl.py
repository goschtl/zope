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
"""

Revision information:
$Id: absoluteurl.py,v 1.10 2003/06/12 09:29:27 jim Exp $
"""

from zope.app import zapi
from zope.publisher.browser import BrowserView
from zope.proxy import sameProxiedObjects

_insufficientContext = ("There isn't enough context to get URL information. "
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

        side_effect_names = dict.get('side_effect_names')
        if side_effect_names:
            url += _side_effects_url(side_effect_names)

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

        side_effect_names = dict.get('side_effect_names')
        if side_effect_names:
            base[-1]['url'] += _side_effects_url(side_effect_names)

        return base

def _side_effects_url(side_effect_names):
    return "/"+"/".join([name
                         for name in side_effect_names
                         if not name.startswith("++vh++")])

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
            side_effect_names = dict.get('side_effect_names')
            if side_effect_names:
                url += _side_effects_url(side_effect_names)
                
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

            side_effect_names = dict.get('side_effect_names')
            if side_effect_names:
                base[-1]['url'] += _side_effects_url(side_effect_names)
                
        return base
