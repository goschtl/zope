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
$Id: AbsoluteURL.py,v 1.6 2002/10/28 07:37:58 stevea Exp $
"""
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.Proxy.ContextWrapper import getWrapperContainer, getInnerWrapperData
from Zope.ComponentArchitecture import getView

from Interface import Interface

class IAbsoluteURL(Interface):

    def __str__():
        """Get a human-readable string representation
        """

    def __repr__():
        """Get a string representation
        """
    
    def __call__():
        """Get a string representation
        """

    def breadcrumbs():
        """Return a tuple like ({'name':name, 'url':url}, ...)

        Name is the name to display for that segment of the breadcrumbs.
        URL is the link for that segment of the breadcrumbs.
        """

class AbsoluteURL(BrowserView):

    def __str__(self):
        context = self.context
        dict = getInnerWrapperData(context)
        name = dict and dict.get('name') or None
        container = getWrapperContainer(context)
        if name is None or container is None:
            raise TypeError, 'Not enough context information to get a URL'
        if name == '.':
            name = dict.get('side_effect_name', name)

        return "%s/%s" % (getView(container, 'absolute_url', self.request),
                          name)

    __call__ = __str__

    def breadcrumbs(self):
        context = self.context
        dict = getInnerWrapperData(context)
        name = dict and dict.get('name') or None
        container = getWrapperContainer(context)
        if name is None or container is None:
            raise TypeError, 'Not enough context information to get a URL'

        if name == '.':
            # The name is meaningless. There is a side-efect name
            # that we need to preserve in the urls (only)
            name = dict.get('side_effect_name', name)
            base = getView(container, 'absolute_url',
                           self.request).breadcrumbs()

            # replace the last step in base with a step with the same
            # name ans an augmented url
            base = base[:-1] + ({
                'name': base[-1]['name'],
                'url': ("%s/%s" % (base[-1]['url'], name)),
                }, )
            return base

        base = getView(container, 'absolute_url', self.request).breadcrumbs()
        base += ({'name': name, 'url': ("%s/%s" % (base[-1]['url'], name))}, )
        return base
        


class SiteAbsoluteURL(BrowserView):

    def __str__(self):
        context = self.context
        dict = getInnerWrapperData(context)
        name = dict and dict.get('name') or None
        if name:
            if name == '.':
                name = dict.get('side_effect_name', name)
            container = getWrapperContainer(context)
            return "%s/%s" % (getView(container, 'absolute_url', self.request),
                              name)
        
        return self.request.getApplicationURL()

    __call__ = __str__

    def breadcrumbs(self):
        context = self.context
        dict = getInnerWrapperData(context)
        name = dict and dict.get('name') or None
        if name:
            # The name is meaningless. There is a side-efect name
            # that we need to preserve in the urls (only)
            if name == '.':
                name = dict.get('side_effect_name', name)
            container = getWrapperContainer(context)
            base = getView(container, 'absolute_url',
                           self.request).breadcrumbs()
            # replace the last step in base with a step with the same
            # name ans an augmented url
            base = base[:-1] + (
                {'name': base[-1]['name'],
                 'url': ("%s/%s" % (base[-1]['url'], name))}, )
            return base

        return ({'name':'', 'url': self.request.getApplicationURL()}, )

        



