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
$Id: ICacheable.py,v 1.4 2002/11/13 11:30:31 ryzaja Exp $
"""
from Interface import Interface
from Zope.ComponentArchitecture import getService
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError
from Zope.ContextWrapper import ContextProperty
import Zope.Schema

class CacheName(Zope.Schema.TextLine):
    """Cache Name"""

    def __allowed(self):
        """Note that this method works only if the Field is context wrapped."""
        try:
            caching_service = getService(self.context, "Caching")
        except ComponentLookupError:
            return ['']
        else:
            return [''] + list(caching_service.getAvailableCaches())

    allowed_values = ContextProperty(__allowed)

class ICacheable(Interface):
    """Object that can be associated with a cache manager."""

    cacheId = CacheName(
        title=u"Cache Name",
        description=u"The name of the cache used for this object.",
        required=True)

    def getCacheId():
        """Gets the associated cache manager ID."""

    def setCacheId(id):
        """Sets the associated cache manager ID."""
