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
$Id: AbsoluteURL.py,v 1.2 2002/06/10 23:29:20 jim Exp $
"""
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.Proxy.ContextWrapper import getWrapperContainer, getWrapperData
from Zope.ComponentArchitecture import getView

from Interface import Interface

class IAbsoluteURL(Interface):

    def __str__():
        """Get a human-readable string representation
        """

    def __repr__():
        """Get a string representation
        """
    

class AbsoluteURL(BrowserView):

    def __str__(self):
        context = self.context
        dict = getWrapperData(context)
        name = dict and dict.get('name') or None
        container = getWrapperContainer(context)
        if name is None or container is None:
            raise TypeError, 'Not enough context information to get a URL'

        return "%s/%s" % (getView(container, 'absolute_url', self.request),
                          name)

    __call__ = __str__


class SiteAbsoluteURL(BrowserView):

    def __str__(self):
        return self.request.getApplicationURL()

    __call__ = __str__


    

