##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
from Products.PluginIndexes.interfaces import IUniqueValueIndex
from Products.PluginIndexes.interfaces import ISortIndex

class IRecentItemsIndex(IUniqueValueIndex, ISortIndex):
    """ API for index returning only "recent" items of a given type.
    """
    def getItemCounts():
        """ Return a mapping of field values => item counts.
        """

    def query(value=None, limit=None, merge=1):
        """ Return a lazy sequence of catalog brains like a catalog search.

        Return results in order, newest first, for the value(s) given.

        If 'value' is omitted, return the most recent for all values.
        
        'limit', if passed, must be an integer value restricting the maximum
        number of results.
        
        If no limit is specified, use the 'max_length' of the index as
        the limit.

        'merge' is a flag:  if true, return a lazy map of the brains.  If
        false, return a sequence of (value, rid, fetch) tuples which can
        be merged later.
        """
