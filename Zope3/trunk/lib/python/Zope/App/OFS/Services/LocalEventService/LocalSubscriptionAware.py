##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

Revision information:
$Id: LocalSubscriptionAware.py,v 1.3 2002/07/11 18:21:31 jim Exp $
"""

from Zope.Event.ISubscriptionAware import ISubscriptionAware
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.App.Traversing import getPhysicalPathString


class LocalSubscriptionAware:
    # a mix-in
    
    __implements__=ISubscriptionAware
    
    def __init__(self):
        self._subscriptions=()
    
    def subscribedTo(self, subscribable, event_type, filter):
        subscribable_path = getPhysicalPathString(subscribable)
        if (subscribable_path, event_type, filter) not in self._subscriptions:
            self._subscriptions+=((subscribable_path,event_type, filter),)
    
    def unsubscribedFrom(self, subscribable, event_type, filter):
        subscribable_path = getPhysicalPathString(subscribable)
        sub=list(self._subscriptions)
        sub.remove((subscribable_path, event_type, filter))
        self._subscriptions=tuple(sub)
        
        
        
