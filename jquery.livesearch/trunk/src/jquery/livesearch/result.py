##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id: layer.py 197 2007-04-13 05:03:32Z rineichen $
"""

import zope.interface
from zope.traversing import api
from zope.traversing.browser import absoluteURL
from zope.security.interfaces import Unauthorized
from zope.security.proxy import removeSecurityProxy

from jquery.livesearch import interfaces


class LiveSearchResultItem(object):
    """Live search result item presentation."""

    zope.interface.implements(interfaces.ILiveSearchResultItem)

    def __init__(self, context):
        """Adatps the object and offers live search result infos.
        
        You need to implement this adapter for your searchable objects.
        """
        self.context = context

    def getURL(self, request):
        return absoluteURL(self.context, request)

    def getText(self):
        """Returns the test used for rendering the link text."""
        try:
            title = getattr(self.context, 'title', None)
        except Unauthorized:
            title = None

        if title is None:
            title = api.getName(self.context)

        return title or u''

    def getScore(self, score):
        """Returns the score."""
        return "%.4f" % score


class LiveSearchResult:
    """Lazily accessed set of object infos."""

    def __init__(self, results, uidutil, request):
        self.results = results
        self.uidutil = uidutil
        self.request = request

    def __len__(self):
        return len(self.results)

    def __iter__(self):
        for uid, score in self.results.items():
            info = {}
            obj = self.uidutil.getObject(uid)
            obj = removeSecurityProxy(obj)
            adapter = interfaces.ILiveSearchResultItem(obj)
            info['obj'] = obj
            info['text'] = adapter.getText()
            info['score'] = adapter.getScore(score)
            info['url'] = adapter.getURL(self.request)
            yield info



