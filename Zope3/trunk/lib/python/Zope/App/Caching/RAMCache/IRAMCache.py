##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""
$Id: IRAMCache.py,v 1.1 2002/10/31 16:01:39 alga Exp $
"""
from Zope.App.Caching.ICache import ICache
from Zope.Event.ISubscriber import ISubscriber
from Interface.Attribute import Attribute

class IRAMCache(ICache, ISubscriber):
    """Interface for the RAM Cache."""

    requestVars = Attribute("""A list of the request variables which
    are automatically added to the key of a cached entry if
    available.""")

    maxEntries = Attribute("""A maximum number of cached values.""")

    maxAge = Attribute("""Maximum age for cached values in seconds.""")

    cleanupInterval = Attribute("""An interval between cache cleanups
    in seconds.""")

    def getStatistics():
        """Reports on the contents of a cache.

        The returned value is a sequence of dictionaries with the
        following keys:

          'path', 'hits', 'misses', 'size', 'counter', 'views',
          'entries'
        """

    def update(request_vars, maxEntries, maxAge, cleanupInterval):
        """Saves the parameters available to the user"""
