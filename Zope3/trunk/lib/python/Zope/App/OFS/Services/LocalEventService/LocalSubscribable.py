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
$Id: LocalSubscribable.py,v 1.4 2002/09/06 02:14:31 poster Exp $
"""

from Zope.Exceptions import NotFoundError
from Zope.Event.ISubscriptionAware import ISubscriptionAware
from Zope.Event.IEvent import IEvent
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Event.Subscribable import Subscribable
from Persistence import Persistent

class LocalSubscribable(Subscribable, Persistent):
    """a local mix-in"""

    def subscribe(wrapped_self,
                  subscriber,
                  event_type=IEvent,
                  filter=None):
        # might be wrapped, might not
        subscriber = removeAllProxies(subscriber)
        
        clean_self = removeAllProxies(wrapped_self)
        wrapped_subscriber = ContextWrapper(subscriber, wrapped_self)
        
        if ISubscriptionAware.isImplementedBy(subscriber):
            wrapped_subscriber.subscribedTo(
                wrapped_self,
                event_type,
                filter)
        
        ev_type = event_type
        if ev_type is IEvent: ev_type = None # optimization
        
        subscribers = clean_self._registry.get(ev_type)
        if subscribers is None:
            subscribers = []
            clean_self._registry.register(ev_type, subscribers)
        subscribers.append((subscriber, filter))

        subs = clean_self._subscribers
        for sub in subs:
            if sub[0] == subscriber:
                sub[1][ev_type] = 1
                break
        else:
            subs.append((subscriber,{ev_type:1}))
        
        clean_self._p_changed = 1 #trigger persistence
        
    
    subscribe=ContextMethod(subscribe)
    
    def unsubscribe(wrapped_self,
                    subscriber,
                    event_type = None,
                    filter = None):
        # subscriber might be wrapped, might not
        subscriber = removeAllProxies(subscriber) 
        
        clean_self = removeAllProxies(wrapped_self)
        wrapped_subscriber = ContextWrapper(subscriber, wrapped_self)
        
        for subscriber_index in range(len(clean_self._subscribers)):
            sub = clean_self._subscribers[subscriber_index]
            if sub[0] == subscriber:
                ev_set = sub[1]
                break
        else:
            raise NotFoundError(subscriber)
        
        
        do_alert = ISubscriptionAware.isImplementedBy(subscriber)
        
        if event_type:
            ev_type = event_type
            if event_type is IEvent:
                ev_type = None # handle optimization
            if ev_type not in ev_set:
                raise NotFoundError(subscriber, event_type, filter)
            subscriptions = clean_self._registry.get(ev_type)
            if not subscriptions:
                raise NotFoundError(subscriber, event_type, filter)
            try:
                subscriptions.remove((subscriber, filter))
            except ValueError:
                raise NotFoundError(subscriber, event_type, filter)
            if do_alert:
                wrapped_subscriber.unsubscribedFrom(
                    wrapped_self, event_type, filter)
            if len(ev_set) == 1:
                for sub in subscriptions:
                    if sub[0] == subscriber:
                        break
                else:
                    del clean_self._subscribers[subscriber_index]
        else:
            for ev_type in ev_set:
                subscriptions = clean_self._registry.get(ev_type)
                subs=subscriptions[:]
                subscriptions[:] = []
                for sub in subs:
                    if sub[0] == subscriber: # deleted (not added back)
                        if do_alert:
                            wrapped_subscriber.unsubscribedFrom(
                                wrapped_self, ev_type or IEvent, sub[1])
                            # IEvent switch is to make optimization
                            # transparent
                    else: # kept (added back)
                        subscriptions.append(sub)
            del clean_self._subscribers[subscriber_index]
        clean_self._p_changed = 1
    
    unsubscribe = ContextMethod(unsubscribe)
