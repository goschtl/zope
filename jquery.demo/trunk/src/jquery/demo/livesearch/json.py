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
from zope.app.catalog.interfaces import ICatalog

from jquery.livesearch.json import JSONLiveSearch


class SampleLiveSearch(JSONLiveSearch):
    """JSON live search method with template for rendering the result."""

    indexName = 'text'

    def getCatalog(self):
        """Returns the right catalog.
        
        Since we have only one search on the demo site, we ignore the searchId.
        """
        return zope.component.getUtility(ICatalog, name='WebSiteCatalog')


class JSONWebSiteLiveSearch(JSONLiveSearch):
    """JSON live search method with template for rendering the result."""

    indexName = 'text'

    def getCatalog(self):
        """Returns the right catalog.
        
        Since we have only one search on the demo site, we ignore the searchId.
        """
        return zope.component.getUtility(ICatalog, name='WebSiteCatalog')

    def getWebSiteLiveSearchResult(self, searchString):
        return super(JSONWebSiteLiveSearch, self).getLiveSearchResult(
            searchString)
