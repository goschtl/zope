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
"""A registration for a cache.

$Id: cache.py,v 1.5 2004/03/01 10:57:38 philikon Exp $
"""
from zope.app.interfaces.services.event import IEventChannel
from zope.app.interfaces.services.service import ISimpleService
from zope.app.cache.interfaces import ICachingService

class ILocalCachingService(ICachingService, IEventChannel):
    """TTW manageable caching service"""
