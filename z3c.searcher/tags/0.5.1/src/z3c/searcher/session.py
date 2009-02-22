##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
$Id:$
"""
__docformat__ = "reStructuredText"

import persistent.dict
import zope.interface
from zope.session.session import Session

from z3c.searcher import interfaces
from z3c.searcher.interfaces import SEARCH_SESSION


class SearchSession(Session):
    """Search session."""

    zope.interface.implementsOnly(interfaces.ISearchSession)

    def __init__(self, request):
        super(SearchSession, self).__init__(request)
        self.searchFilters = persistent.dict.PersistentDict()

    def getFilter(self, name, key='default'):
        """Return search filter by name."""
        spd = self.__getitem__(SEARCH_SESSION)
        filterList = spd.get(name, None)
        if filterList is None:
            spd[name] = persistent.dict.PersistentDict()
            filterList = spd.get(name)
        return filterList.get(key)

    def getFilters(self, key='default'):
        """Return a list of search filters."""
        spd = self.__getitem__(SEARCH_SESSION)
        filters = []
        append = filters.append
        for filterList in spd.values():
            filter = filterList.get(key)
            if filter is not None:
                append(filter)
        return filters

    def addFilter(self, name, searchFilter, key='default'):
        """Add search filter.
        
        Note: this session doesn't know about the context, this means you need
        to locate the added filter after you where adding it. Otherwise you 
        will get security problems because of the missing location.
        """
        spd = self.__getitem__(SEARCH_SESSION)
        filterList = spd.get(name)
        if filterList is None:
            spd[name] = persistent.dict.PersistentDict()
            filterList = spd.get(name)
        filterList[key] = searchFilter

    def removeFilter(self, name, key='default'):
        """Remove search filter."""
        spd = self.__getitem__(SEARCH_SESSION)
        filterList = spd.get(name)
        if filterList is not None:
            del filterList[key]
