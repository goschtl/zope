##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""Specific HTTP

$Id$
"""
from zope.interface import implements
from zope.proxy import removeAllProxies
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.app.traversing.interfaces import TraversalError

from zope.app import zapi
from zope.app.traversing.api import getParent
from zope.app.traversing.namespace import UnexpectedParameters
from zope.app.traversing.interfaces import ITraversable

from zwiki.interfaces import IWikiPage, IWikiPageHierarchy

class WikiPageTraverser:
    implements(IPublishTraverse)
    __used_for__ = IWikiPage

    def __init__(self, page, request):
        self.context = page
        self.wiki = getParent(page)
        self.request = request

    def publishTraverse(self, request, name):
        page = self.wiki.get(name, None)
        
        # Check that page has self.context as parent
        if page is None or \
           not zapi.getName(self.context) in IWikiPageHierarchy(page).parents:

            view = zapi.queryMultiAdapter((self.context, request), name=name)
            if view is not None:
                return view

            raise NotFound(self.context, name, request)


        return removeAllProxies(page)

    def browserDefault(self, request):
        c = self.context
        view_name = zapi.getDefaultViewName(c, request)
        view_uri = "@@%s" % view_name
        return c, (view_uri,)


_marker = object()

class WikiPageTraversable:
    """Traverses wikipages via wiki itself and getattr.
    """

    implements(ITraversable)
    __used_for__ = IWikiPage

    def __init__(self, page):
        self._page = page
        self._wiki = getParent(page)


    def traverse(self, name, furtherPath):
        subobj = self._wiki.get(name, _marker)
        if subobj is _marker:
            subobj = getattr(self._page, name, _marker)
            if subobj is _marker:
                raise TraversalError, name

        return subobj
