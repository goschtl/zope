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
$Id: LocalSubscribable.py,v 1.7 2002/12/12 20:05:51 jack-e Exp $
"""

from Zope.Exceptions import NotFoundError
from Zope.Event.ISubscriptionAware import ISubscriptionAware
from Zope.Event.IEvent import IEvent
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Event.Subscribable import Subscribable
from Persistence import Persistent
from Zope.App.Traversing import traverse, getPhysicalPathString
from Zope.App.Traversing import locationAsUnicode

class LocalSubscribable(Persistent, Subscribable):
    """a local mix-in"""
    
    __implements__ = (
        Subscribable.__implements__,
        Persistent.__implements__)
    
    # uses (and needs) __init__ from Zope.Event.Subscribable

    def subscribe(wrapped_self,
                  subscriber,
                  event_type=IEvent,
                  filter=None):
        
        # subscriber needs to be wrapped
        subscriber_path = getPhysicalPathString(subscriber)
       
        clean_self = removeAllProxies(wrapped_self)
        
        if ISubscriptionAware.isImplementedBy(subscriber):
            subscriber.subscribedTo(
                wrapped_self,
                event_type,
                filter)
        
        ev_type = event_type
        if ev_type is IEvent: ev_type = None # optimization
        
        subscribers = clean_self._registry.get(ev_type)
        if subscribers is None:
            subscribers = []
            clean_self._registry.register(ev_type, subscribers)
        # XXX subscriber_path
        subscribers.append((subscriber_path, filter))

        subs = clean_self._subscribers
        for sub in subs:
            # XXX subscriber_path
            if sub[0] == subscriber_path:
                sub[1][ev_type] = 1
                break
        else:
            # XXX subscriber_path
            subs.append((subscriber_path,{ev_type:1}))
        
        clean_self._p_changed = 1 #trigger persistence
        # XXX should this and similar be done earlier in the method?
        # XXX Ask Shane
        
    
    subscribe=ContextMethod(subscribe)
    
    def unsubscribe(wrapped_self,
                    subscriber,
                    event_type = None,
                    filter = None):
        # subscriber must be wrapped
        subscriber_path = getPhysicalPathString(subscriber)
        
        clean_self = removeAllProxies(wrapped_self)
        
        for subscriber_index in range(len(clean_self._subscribers)):
            sub = clean_self._subscribers[subscriber_index]
            # XXX subscriber_path
            if sub[0] == subscriber_path:
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
                # XXX subscriber_path
                subscriptions.remove((subscriber_path, filter))
            except ValueError:
                raise NotFoundError(subscriber, event_type, filter)
            if do_alert:
                subscriber.unsubscribedFrom(
                    wrapped_self, event_type, filter)
            if len(ev_set) == 1:
                for sub in subscriptions:
                    # XXX subscriber_path
                    if sub[0] == subscriber_path:
                        break
                else:
                    del clean_self._subscribers[subscriber_index]
        else:
            for ev_type in ev_set:
                subscriptions = clean_self._registry.get(ev_type)
                subs=subscriptions[:]
                subscriptions[:] = []
                for sub in subs:
                    # XXX subscriber_path
                    if sub[0] == subscriber_path: # deleted (not added back)
                        if do_alert:
                            subscriber.unsubscribedFrom(
                                wrapped_self, ev_type or IEvent, sub[1])
                            # IEvent switch is to make optimization
                            # transparent
                    else: # kept (added back)
                        subscriptions.append(sub)
            del clean_self._subscribers[subscriber_index]
        clean_self._p_changed = 1
        # XXX should be done earlier?  Ask Shane
    
    unsubscribe = ContextMethod(unsubscribe)

    def listSubscriptions(self, subscriber, event_type=None):
        # subscriber must be wrapped
        subscriber_path = getPhysicalPathString(subscriber)
        
        result=[]
        if event_type:
            ev_type=event_type
            if event_type is IEvent:
                ev_type=None # handle optimization
            subscriptions = self._registry.get(ev_type)
            if subscriptions:
                for sub in subscriptions:
                    # XXX subscriber_path
                    if sub[0]==subscriber_path:
                        result.append((event_type, sub[1]))
        else:
            for subscriber_index in range(len(self._subscribers)):
                sub=self._subscribers[subscriber_index]
                # XXX subscriber_path
                if sub[0]==subscriber_path:
                    ev_set=sub[1]
                    break
            else:
                return result
            for ev_type in ev_set:
                subscriptions = self._registry.get(ev_type)
                if subscriptions:
                    for sub in subscriptions:
                        # XXX subscriber_path
                        if sub[0]==subscriber_path:
                            result.append((ev_type or IEvent, sub[1]))
        return result
