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
$Id: AbsoluteURL.py,v 1.3 2002/07/11 19:33:58 jim Exp $
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


class AbsoluteURL(BrowserView):

    def __str__(self):
        context = self.context
        dict = getInnerWrapperData(context)
        name = dict and dict.get('name') or None
        container = getWrapperContainer(context)
        if name is None or container is None:
            raise TypeError, 'Not enough context information to get a URL'

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

        base = getView(container, 'absolute_url', self.request).breadcrumbs()
        base += ({'name': name, 'url': ("%s/%s" % (base[-1]['url'], name))}, )
        return base
        


class SiteAbsoluteURL(BrowserView):

    def __str__(self):
        return self.request.getApplicationURL()

    __call__ = __str__

    def breadcrumbs(self):
        return ({'name':'', 'url': self.request.getApplicationURL()}, )

        
