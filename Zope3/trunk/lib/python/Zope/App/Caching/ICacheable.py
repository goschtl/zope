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
$Id: ICacheable.py,v 1.2 2002/10/09 13:08:44 alga Exp $
"""
from Interface import Interface
from Zope.ContextWrapper import ContextMethod
from Zope.ComponentArchitecture import getService
import Zope.Schema

class CacheName(Zope.Schema.Text):
    """Cache Name"""

    def items(self):
        """Note that this method works only if the Field is context wrapped."""
        caching_service = getService(self, "Caching")
        return [('', '(None)')] + caching_service.getAvailableCaches() # FIXME: i18n

    items = ContextMethod(items)

class ICacheable(Interface):
    """Object that can be associated with a cache manager."""

    cacheId = CacheName(title=u"Cache Name",
                        description=u"The name of the cache used for this object.",
                        required=False)

    def getCacheId():
        """Gets the associated cache manager ID."""

    def setCacheId(id):
        """Sets the associated cache manager ID."""
