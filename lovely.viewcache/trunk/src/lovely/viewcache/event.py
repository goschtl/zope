##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
$Id$
"""
__docformat__ = 'restructuredtext'

from zope import interface
from zope import component

from zope.proxy import removeAllProxies

from zope.app.intid.interfaces import IIntIds

from lovely.viewcache.interfaces import IViewCache


def invalidateCache(obj, event):
    cache = component.queryUtility(IViewCache)
    if cache is None:
        return
    deps = [removeAllProxies(iface) for iface in interface.providedBy(obj)]
    intids = component.queryUtility(IIntIds, context=obj)
    if intids is not None:
        uid = intids.queryId(obj)
        if uid is not None:
            deps.append(uid)
    if deps:
        cache.invalidate(dependencies=deps)

