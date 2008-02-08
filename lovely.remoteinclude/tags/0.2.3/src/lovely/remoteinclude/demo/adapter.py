##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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

from zope import component
from zope import event

from zope.proxy import removeAllProxies
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from lovely.memcached.event import InvalidateCacheEvent


@component.adapter(IObjectModifiedEvent)
def objectModified(ev):
    event.notify(InvalidateCacheEvent(dependencies=[removeAllProxies(ev.object)]))

