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
$Id: ICacheable.py,v 1.1 2002/10/03 09:41:23 mgedmin Exp $
"""
from Interface import Interface

class ICacheable(Interface):
    """Object that can be associated with a cache manager."""

    def getCacheId():
        """Gets the associated cache manager ID."""

    def setCacheId(id):
        """Sets the associated cache manager ID."""
