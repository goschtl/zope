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
$Id: LocalServiceSubscribable.py,v 1.9 2002/12/12 20:05:51 jack-e Exp $
"""

from Zope.Exceptions import NotFoundError
from Zope.Event.ISubscriptionAware import ISubscriptionAware
from Zope.Event.IEvent import IEvent
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.Proxy.ContextWrapper import ContextWrapper
from LocalSubscribable import LocalSubscribable
from Zope.App.ComponentArchitecture.NextService import getNextService, queryNextService
from Zope.App.Traversing import getPhysicalPathString

class LocalServiceSubscribable(LocalSubscribable):
    """a local mix-in for services"""
    
    __implements__ = LocalSubscribable.__implements__
    
    _serviceName = None # should be replaced; usually done in "bound"
                        # method of a subclass
    
    # uses (and needs) __init__ from Zope.Event.Subscribable (via
    # LocalSubscribable)
    
    def unsubscribe(wrapped_self,
                    subscriber,
                    event_type=None,
                    filter=None):
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
            # raise NotFoundError(subscriber)
            next_service = queryNextService(wrapped_self, clean_self._serviceName)
            if next_service is not None:
                next_service.unsubscribe(subscriber, event_type, filter)
            return
        
        
        do_alert = ISubscriptionAware.isImplementedBy(subscriber)
        
        if event_type:
            # we only have to clean the one event_type out
            ev_type = event_type
            if event_type is IEvent:
                ev_type = None # *** handle optimization: a subscription
                # to IEvent is a subscription to all events; this is
                # converted to 'None' so that the _registry can
                # shortcut some of its tests
            if ev_type not in ev_set:
                next_service = queryNextService(wrapped_self, clean_self._serviceName)
                if next_service is not None:
                    next_service.unsubscribe(subscriber, event_type, filter)
            else:
                subscriptions = clean_self._registry.get(ev_type)
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
            # we have to clean all the event types out (ignoring filter)
            for ev_type in ev_set:
                subscriptions = clean_self._registry.get(ev_type)
                subs = subscriptions[:]
                subscriptions[:] = []
                for sub in subs:
                    # XXX subscriber_path
                    if sub[0] == subscriber_path: # deleted (not added back)
                        if do_alert:
                            subscriber.unsubscribedFrom(
                                wrapped_self, ev_type or IEvent, sub[1])
                            # IEvent switch is to make optimization
                            # transparent (see *** comment above in
                            # this method)
                    else: # kept (added back)
                        subscriptions.append(sub)
            del clean_self._subscribers[subscriber_index]
            next_service = queryNextService(wrapped_self, clean_self._serviceName)
            if next_service is not None:
                next_service.unsubscribe(subscriber, event_type, filter)
        clean_self._p_changed = 1 #trigger persistence
    unsubscribe = ContextMethod(unsubscribe)
    
    def listSubscriptions(wrapped_self, subscriber, event_type=None):
        # subscriber must be wrapped
       
        clean_self = removeAllProxies(wrapped_self)
        result = LocalSubscribable.listSubscriptions(
            clean_self, subscriber, event_type)
        next_service = queryNextService(wrapped_self, clean_self._serviceName)
        if next_service is not None:
            result.extend(next_service.listSubscriptions(subscriber,
                                                         event_type))
        return result
    listSubscriptions = ContextMethod(listSubscriptions)
