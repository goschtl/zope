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

import zope.component
import zope.interface
from zope.pagetemplate.interfaces import IPageTemplate
from zope.app.catalog.interfaces import ICatalog
from zope.app.intid.interfaces import IIntIds

from z3c.template.template import getPageTemplate
from zif.jsonserver.jsonrpc import MethodPublisher
from zif.jsonserver.interfaces import IJSONRPCRequest

from jquery.livesearch import interfaces
from jquery.livesearch.result import LiveSearchResult


class JSONLiveSearch(MethodPublisher):
    """JSON live search method with template for rendering the result."""

    zope.interface.implements(interfaces.IJSONLiveSearch)
    zope.component.adapts(zope.interface.Interface, IJSONRPCRequest)

    # get the registered IPageTemplate template
    template = getPageTemplate()
    indexName = 'TextIndex'
    jsonID = None # the json request id set in the javascript

    def __init__(self, context, request):
        super(JSONLiveSearch, self).__init__(context, request)
        self.searchString = None
        self.results = ()

    def getCatalog(self):
        """Returns the right catalog."""
        return zope.component.getUtility(ICatalog)

    def getLiveSearchResult(self, searchString):
        """Returns JSON like dict/array containing a content attribute with the 
        search result.
        """
        self.jsonID = self.request.jsonID
        self.doSearch(searchString)
        # return None for content variable if no result was found. This will 
        # intepreted via JSON as null in javascript.
        if len(self.results) == 0:
            return {'content':None}
        # render template only if result was found
        else:
            return {'content':self.render()}

    def doSearch(self, searchString):
        """Search the catalog for items and set the results."""
        catResults = None
        if searchString is not None:
            catalog = self.getCatalog()
            liveSearchString = searchString + '*'
            if liveSearchString.strip('* ') != '':
                catResults = catalog.apply({self.indexName:liveSearchString})
        if catResults is not None:
            uidutil = zope.component.getUtility(IIntIds)
            self.results = LiveSearchResult(catResults, uidutil, self.request)

    def getResults(self):
        return self.results

    def render(self):
        # render live search results
        template = zope.component.getMultiAdapter((self, self.request), 
            IPageTemplate)
        return template(self)
