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
$Id: ICache.py,v 1.1 2002/10/03 09:41:23 mgedmin Exp $
"""
from Interface import Interface

class ICache(Interface):
    """Interface for caches."""

    def invalidate(ob, view_name=None, keywords=None):
        """Invalidates cached entries that apply to the given object.

        If view_name is specified, only invalidates entries for that
        view.  If keywords is also specified, only invalidates entries
        for that view and given keywords.  Otherwise, if view_name is
        None, invalidates all entries for the object.
        """

    def query(ob, view_name="", keywords=None, mtime_func=None, default=None)
        """Returns the cached data previously stored by set().

        ob is the content object from which the object ID, modification
        times, and acquisition context are usually determined. view_name is
        the name of the view or method used to display the content object.
        keywords is a set of filtered keywords and values which should all
        be used to select a cache entry. mtime_func is an optional function
        that will be called to determine the content modification time
        based on more intimate knowledge of the cached object.
        """

    def set(data, ob, view_name="", keywords=None, mtime_func=None):
        """Stores the result of executing an operation."""

