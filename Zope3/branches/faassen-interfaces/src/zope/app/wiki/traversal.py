##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""Specific HTTP

$Id: traversal.py,v 1.4 2004/04/17 17:15:35 jim Exp $
"""
from zope.interface import implements
from zope.proxy import removeAllProxies
from zope.component import getDefaultViewName, queryView
from zope.publisher.interfaces import IPublishTraverse
from zope.exceptions import NotFoundError

from zope.app.traversing import getParent
from zope.app.traversing.namespace import UnexpectedParameters
from zope.app.traversing.interfaces import ITraversable
from zope.app.wiki.interfaces import IWikiPage

class WikiPageTraverser:
    implements(IPublishTraverse)
    __used_for__ = IWikiPage

    def __init__(self, page, request):
        self.context = page
        self.wiki = getParent(page)
        self.request = request

    def publishTraverse(self, request, name):
        subob = self.wiki.get(name, None)

        # XXX: Check that subobj has self.context as parent!
        if subob is None:

            view = queryView(self.context, name, request)
            if view is not None:
                return view

            raise NotFoundError(self.context, name, request)

        return removeAllProxies(subob)

    def browserDefault(self, request):
        c = self.context
        view_name = getDefaultViewName(c, request)
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
                raise NotFoundError, name

        return subobj
