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
$Id: subs.py,v 1.1 2002/12/30 14:03:02 stevea Exp $
"""
from __future__ import generators
from zope.exceptions import NotFoundError
from persistence import Persistent
from types import StringTypes

from zope.proxy.context import ContextMethod
from zope.proxy.introspection import removeAllProxies

from zope.app.traversing import getPhysicalPathString
from zope.app.traversing import locationAsUnicode, getPhysicalPath, traverse
from zope.app.interfaces.event import IEvent, ISubscriber, ISubscribable
from zope.app.interfaces.event import ISubscribingAware

from zope.component import getService, getAdapter
from zope.interface.type import TypeRegistry

__metaclass__ = type

try:
    enumerate # python 2.3
except NameError:
    def enumerate(collection):
        'Generates an indexed series:  (0,coll[0]), (1,coll[1]) ...'     
        i = 0
        it = iter(collection)
        while 1:
            yield (i, it.next())
            i += 1

class Subscribable(Persistent):
    """A local mix-in"""
    
    __implements__ = ISubscribable
    
    def __init__(self):
        self._registry = TypeRegistry()
        # using a list rather than a dict so that subscribers may define
        # custom __eq__ methods
        self._subscribers = []
        
    def subscribe(wrapped_self, subscriber, event_type=IEvent, filter=None):
        '''See ISubscribable'''
        clean_subObj = removeAllProxies(subscriber)
        if isinstance(clean_subObj, int):
            hub = getService(wrapped_self, "HubIds")
            subObj = hub.getObject(subscriber)
            clean_subObj = removeAllProxies(subObj)
        elif isinstance(clean_subObj, StringTypes):
            subObj = traverse(wrapped_self, subscriber)
            clean_subObj = removeAllProxies(subObj)
            subscriber = locationAsUnicode(subscriber)
        else:
            subObj = subscriber
            hub = getService(wrapped_self, "HubIds")
            try:
                subscriber = hub.getHubId(subObj)
            except NotFoundError:
                # XXX this should be superfluous. getPhysicalPathString should
                #     always return a canonical path.
                subscriber = locationAsUnicode(
                    getPhysicalPath(subscriber))
        
        if ISubscribingAware.isImplementedBy(clean_subObj):
            subObj.subscribedTo(wrapped_self, event_type, filter)
        
        ev_type = event_type
        if ev_type is IEvent:
            ev_type = None  # optimization
        clean_self = removeAllProxies(wrapped_self)
        
        clean_self._p_changed = 1
        
        subscribers = clean_self._registry.get(ev_type)
        if subscribers is None:
            subscribers = []
            clean_self._registry.register(ev_type, subscribers)
        subscribers.append((subscriber, filter))

        subs = clean_self._subscribers
        for sub in subs:
            if sub[0] == subscriber:
                try:
                    sub[1][ev_type] += 1
                except KeyError:
                    sub[1][ev_type] = 1
                break
        else:
            subs.append((subscriber,{ev_type:1}))
        
        return subscriber
    subscribe = ContextMethod(subscribe)
    
    def _getSubscribers(clean_self, wrapped_self, subscriber):
        subscribers = []
        # XXX This comment needs explanation:
        # shortcut; useful for notify
        if wrapped_self is clean_self: 
            return [subscriber], None, None
        clean_subObj = removeAllProxies(subscriber)
        if isinstance(clean_subObj, int):
            hub = getService(wrapped_self, "HubIds")
            try:
                subObj = hub.getObject(subscriber)
            except NotFoundError:
                subObj = None
            else:
                clean_subObj = removeAllProxies(subObj)
            subscribers.append(subscriber)
        elif isinstance(clean_subObj, StringTypes):
            try:
                subObj = traverse(wrapped_self, subscriber)
            except NotFoundError:
                subObj = None
            else:
                clean_subObj = removeAllProxies(subObj)
            subscribers.append(locationAsUnicode(subscriber))
        else:
            subObj = subscriber
            hub = getService(wrapped_self, "HubIds")
            try:
                subscribers.append(hub.getHubId(subObj))
            except NotFoundError:
                pass
            subscribers.append(locationAsUnicode(
                getPhysicalPath(subscriber)))
        return subscribers, clean_subObj, subObj
    
    def _getEventSets(self, subscribers):
        ev_sets = {}
        for self_ix, sub in enumerate(self._subscribers):
            for arg_ix, subscriber in enumerate(subscribers):
                if sub[0] == subscriber:
                    ev_sets[(subscriber, self_ix)] = sub[1]
                    del subscribers[arg_ix]
                    break
            if not subscribers:
                break
        else:
            if len(ev_sets.keys()) == 0:
                raise NotFoundError(subscribers)
        return ev_sets
    
    def _cleanAllForSubscriber(clean_self,
                               wrapped_self,
                               ev_sets,
                               do_alert,
                               subObj):
        for (subscriber, subscriber_index), ev_set in ev_sets.items():
            for ev_type in ev_set:
                subscriptions = clean_self._registry.get(ev_type)
                if ev_type is None:
                    ev_type = IEvent
                subs = subscriptions[:]
                subscriptions[:] = []
                for sub in subs:
                    if sub[0] == subscriber:  # deleted (not added back)
                        if do_alert:
                            subObj.unsubscribedFrom(
                                wrapped_self, ev_type, sub[1]
                                )
                    else: # kept (added back)
                        subscriptions.append(sub)
            del clean_self._subscribers[subscriber_index]
    
    def unsubscribe(wrapped_self, subscriber, event_type=None, filter=None):
        '''See ISubscribable'''
        clean_self = removeAllProxies(wrapped_self)
        subscribers, clean_subObj, subObj = clean_self._getSubscribers(
            wrapped_self, subscriber)
        
        ev_sets = clean_self._getEventSets(subscribers)
        
        do_alert = (subObj is not None and
                    ISubscribingAware.isImplementedBy(clean_subObj)
                   )
        
        clean_self._p_changed = 1
        
        if event_type:
            # we have to clean out one and only one subscription of this
            # subscriber for event_type, filter (there may be more,
            # even for this exact combination of subscriber,
            # event_type, filter; we only do *one*)
            ev_type = event_type
            if event_type is IEvent:
                ev_type = None
                # *** handle optimization: a subscription to IEvent is a
                # subscription to all events; this is converted to 'None'
                # so that the _registry can shortcut some of its tests
            for (subscriber, subscriber_index), ev_set in ev_sets.items():
                if ev_type in ev_set:
                    subscriptions = clean_self._registry.get(ev_type)
                    if subscriptions:
                        try:
                            subscriptions.remove((subscriber, filter))
                        except ValueError:
                            pass
                        else:
                            if do_alert:
                                subObj.unsubscribedFrom(
                                    wrapped_self, event_type, filter)
                            ev_set[ev_type] -= 1
                            if ev_set[ev_type] < 1:
                                for sub in subscriptions:
                                    if sub[0] == subscriber:
                                        break
                                else:
                                    if len(ev_set) > 1:
                                        del ev_set[ev_type]
                                    else:  # len(ev_set) == 1
                                        del clean_self._subscribers[
                                            subscriber_index]
                            break
            else:
                raise NotFoundError(subscriber, event_type, filter)
        else:
            # we have to clean all the event types out (ignoring filter)
            clean_self._cleanAllForSubscriber(wrapped_self,
                                              ev_sets,
                                              do_alert,
                                              subObj)
    unsubscribe = ContextMethod(unsubscribe)

    def listSubscriptions(wrapped_self, subscriber, event_type=None):
        '''See ISubscribable'''
        clean_self = removeAllProxies(wrapped_self)
        subscribers, clean_subObj, subObj = clean_self._getSubscribers(
            wrapped_self, subscriber)
        
        result=[]
        if event_type:
            ev_type=event_type
            if event_type is IEvent:
                ev_type=None  # handle optimization
            subscriptions = self._registry.get(ev_type)
            if subscriptions:
                for sub in subscriptions:
                    for subscriber in subscribers:
                        if sub[0]==subscriber:
                            result.append((event_type, sub[1]))
        else:
            try:
                ev_sets = clean_self._getEventSets(subscribers)
            except NotFoundError:
                return result
            for (subscriber, subscriber_index), ev_set in ev_sets.items():
                for ev_type in ev_set:
                    subscriptions = self._registry.get(ev_type)
                    if subscriptions:
                        if ev_type is None:
                            ev_type = IEvent
                        for sub in subscriptions:
                            if sub[0]==subscriber:
                                result.append((ev_type, sub[1]))
        return result
    listSubscriptions = ContextMethod(listSubscriptions)


class SubscriptionTracker:
    "Mix-in for subscribers that want to know to whom they are subscribed"
    
    __implements__ = ISubscribingAware
    
    def __init__(self):
        self._subscriptions = ()
    
    def subscribedTo(self, subscribable, event_type, filter):
        # XXX insert super() call here
        # This raises an error for subscriptions to global event service.
        subscribable_path = getPhysicalPathString(subscribable)
        if (subscribable_path, event_type, filter) not in self._subscriptions:
            self._subscriptions += ((subscribable_path, event_type, filter),)
    
    def unsubscribedFrom(self, subscribable, event_type, filter):
        # XXX insert super() call here
        # This raises an error for subscriptions to global event service.
        subscribable_path = getPhysicalPathString(subscribable)
        sub = list(self._subscriptions)
        sub.remove((subscribable_path, event_type, filter))
        self._subscriptions = tuple(sub)

