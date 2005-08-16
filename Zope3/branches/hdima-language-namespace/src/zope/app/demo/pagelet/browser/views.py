##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Pagelet Demo

$Id$
"""
__docformat__ = 'restructuredtext'


from zope.interface import implements

from zope.app.publisher.browser import BrowserView

from zope.app.pagelet.interfaces import IPageData
from zope.app.demo.pagelet.interfaces import IPageletContent



class DemoPageData(object):
    """Provide an page data class where we use in pagelet."""

    implements(IPageData)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view
        
    def title(self):
        return "DemoPageData title"
        
    def description(self):
        return "A hardcoded title from the DemoPageData"



class PageletContentView(BrowserView):
    """Provide an index view for PageletContent."""

    __used_for__ = IPageletContent

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def title(self):
        return self.context.title
        
    def description(self):
        return self.context.description
