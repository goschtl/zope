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
$Id: ICachingService.py,v 1.1 2002/10/03 09:41:23 mgedmin Exp $
"""
from Interface import Interface

class ICachingService(Interface):

    def getCache(name):
        """Returns a cache object by name."""

    def queryCache(name, default):
        """Return a cache object by name or default."""

    def getAvailableCaches():
        """Returns a list of names of cache objects known to this caching service."""



