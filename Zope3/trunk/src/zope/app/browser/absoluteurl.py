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
$Id: absoluteurl.py,v 1.5 2003/04/28 13:14:19 mgedmin Exp $
"""
from zope.publisher.browser import BrowserView
from zope.proxy.context import getWrapperContainer, getInnerWrapperData
from zope.proxy.introspection import removeAllProxies
from zope.component import getView

class AbsoluteURLBase(BrowserView):

    def __str__(self):
        context = self.context
        vh_root = removeAllProxies(self.request.getVirtualHostRoot())
        if removeAllProxies(context) is vh_root:
            return self.request.getApplicationURL()
        container = getWrapperContainer(context)
        container_url = str(getView(container, 'absolute_url',
                                    self.request))
        dict = getInnerWrapperData(context)
        name = dict and dict.get('name') or None
        if name == '.':
            name = dict.get('side_effect_name', name)
            if name.startswith('++vh++'):
                return container_url
        return "%s/%s" % (container_url, name)

    def breadcrumbs(self):
        context = self.context
        vh_root = removeAllProxies(self.request.getVirtualHostRoot())
        if removeAllProxies(context) is vh_root:
            return ({'name':'', 'url': self.request.getApplicationURL()}, )
        dict = getInnerWrapperData(context)
        name = dict and dict.get('name') or None
        container = getWrapperContainer(context)
        base = getView(container, 'absolute_url', self.request).breadcrumbs()

        if name == '.':
            # The name is meaningless. There is a side-efect name
            # that we need to preserve in the urls (only)
            name = dict.get('side_effect_name', name)
            if name.startswith('++vh++'):
                return base

            # replace the last step in base with a step with the same
            # name and an augmented url
            base = base[:-1] + (
                {'name': base[-1]['name'],
                 'url': ("%s/%s" % (base[-1]['url'], name))}, )
            return base

        base += ({'name': name, 'url': ("%s/%s" % (base[-1]['url'], name))}, )
        return base


class AbsoluteURL(AbsoluteURLBase):

    def __str__(self):
        dict = getInnerWrapperData(self.context)
        name = dict and dict.get('name') or None
        container = getWrapperContainer(self.context)
        if name is None or container is None:
            raise TypeError, 'Not enough context information to get a URL'
        return super(AbsoluteURL, self).__str__()

    __call__ = __str__

    def breadcrumbs(self):
        context = self.context
        dict = getInnerWrapperData(context)
        name = dict and dict.get('name') or None
        container = getWrapperContainer(context)
        if name is None or container is None:
            raise TypeError, 'Not enough context information to get a URL'

        return super(AbsoluteURL, self).breadcrumbs()


class SiteAbsoluteURL(AbsoluteURLBase):

    def __str__(self):
        dict = getInnerWrapperData(self.context)
        name = dict and dict.get('name') or None
        if name:
            return super(SiteAbsoluteURL, self).__str__()
        return self.request.getApplicationURL()

    __call__ = __str__

    def breadcrumbs(self):
        context = self.context
        dict = getInnerWrapperData(context)
        name = dict and dict.get('name') or None
        if name:
            return super(SiteAbsoluteURL, self).breadcrumbs()
        return ({'name':'', 'url': self.request.getApplicationURL()}, )
