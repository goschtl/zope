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
"""mix-in for subscribers that want to know to whom they are subscribed

Revision information:
$Id: LocalSubscriptionAware.py,v 1.4 2002/10/21 06:14:46 poster Exp $
"""

from Zope.Event.ISubscriptionAware import ISubscriptionAware
from Zope.App.Traversing import getPhysicalPathString


class LocalSubscriptionAware:
    "mix-in for subscribers that want to know to whom they are subscribed"
    
    __implements__=ISubscriptionAware
    
    def __init__(self):
        self._subscriptions=()
    
    def subscribedTo(self, subscribable, event_type, filter):
        # This breaks for subscriptions to global event service.
        # Unless the global event service becomes persistent, this
        # is probably correct behavior.
        subscribable_path = getPhysicalPathString(subscribable)
        if (subscribable_path, event_type, filter) not in self._subscriptions:
            self._subscriptions+=((subscribable_path,event_type, filter),)
    
    def unsubscribedFrom(self, subscribable, event_type, filter):
        # global event service breaks, as above
        subscribable_path = getPhysicalPathString(subscribable)
        sub=list(self._subscriptions)
        sub.remove((subscribable_path, event_type, filter))
        self._subscriptions=tuple(sub)
        
        
        
