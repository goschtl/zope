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
$Id: ICache.py,v 1.5 2002/12/12 15:28:15 mgedmin Exp $
"""
from Interface import Interface

class ICache(Interface):
    """Interface for caches."""

    def invalidate(ob, key=None):
        """Invalidates cached entries that apply to the given object.

        ob is an object location.  If key is specified, only
        invalidates entry for the given key.  Otherwise invalidates
        all entries for the object.
        """

    def invalidateAll():
        """Invalidates all cached entries."""

    def query(ob, key=None, default=None):
        """Returns the cached data previously stored by set().

        ob is the location of the content object being cached.  key is
        a mapping of keywords and values which should all be used to
        select a cache entry.
        """

    def set(data, ob, key=None):
        """Stores the result of executing an operation."""

