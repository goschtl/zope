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
$Id: LocalEventService.py,v 1.4 2002/08/01 15:33:43 jim Exp $
"""

from Zope.Event.GlobalEventService import eventService
from Zope.Event.IEvent import IEvent
from Zope.Event.IEventService import IEventService
from Zope.Event.ISubscriber import ISubscriber
from Zope.Event.ISubscriptionAware import ISubscriptionAware

from Zope.App.OFS.Services.ServiceManager.IBindingAware import IBindingAware
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.ComponentArchitecture import getNextService, getAdapter, getService
from Zope.ContextWrapper import ContextMethod
from Zope.Exceptions import NotFoundError
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Proxy.ProxyIntrospection import removeAllProxies

from PathSubscriber import PathSubscriber
from LocalSubscriptionAware import LocalSubscriptionAware
from LocalServiceSubscribable import LocalServiceSubscribable

from Interface.Attribute import Attribute

class ILocalEventService(
    IEventService, ISubscriber, IBindingAware, ISubscriptionAware):
    
    def isPromotableEvent(event):
        """a hook.  Returns a true value if, when publishing an
        event, the event should also be promoted to the
        next (higher) level of event service, and a false value
        otherwise.  The default implementation is to always return
        true."""
    
    subscribeOnBind=Attribute(
        """if true, event service will subscribe
        to the parent event service on binding, unless the parent
        service is the global event service""")

class LocalEventService(LocalServiceSubscribable, LocalSubscriptionAware):
        
    __implements__ = ILocalEventService
    
    _serviceName="Events" # used by LocalServiceSubscribable
    
    subscribeOnBind=1
    
    def __init__(self):
        LocalServiceSubscribable.__init__(self)
        LocalSubscriptionAware.__init__(self)
    
    def isPromotableEvent(self, event):
        "see ILocalEventService"
        return 1
    
    def publishEvent(wrapped_self, event):
        "see IEventService"
        clean_self=removeAllProxies(wrapped_self)
        
        subscriptionses = clean_self._registry.getAllForObject(event)

        for subscriptions in subscriptionses:
            
            for subscriber,filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                ContextWrapper(subscriber, wrapped_self).notify(event)
        publishedEvents=getattr(clean_self, "_v_publishedEvents", None)
        if publishedEvents is None:
            publishedEvents=clean_self._v_publishedEvents=[event]
        else: publishedEvents.append(event)
        if(clean_self.isPromotableEvent(event)):
            getNextService(wrapped_self, 'Events').publishEvent(event)
        publishedEvents.remove(event)
    
    publishEvent=ContextMethod(publishEvent)
        
    def notify(wrapped_self, event):
        "see ISubscriber"
        clean_self=removeAllProxies(wrapped_self)
        publishedEvents=getattr(clean_self, "_v_publishedEvents", None)
        if publishedEvents is None or event not in publishedEvents:
        
            subscriptionses = clean_self._registry.getAllForObject(event)

            for subscriptions in subscriptionses:
                
                for subscriber,filter in subscriptions:
                    if filter is not None and not filter(event):
                        continue
                    ContextWrapper(subscriber, wrapped_self).notify(event)
    
    notify=ContextMethod(notify)
    
    
    def bound(wrapped_self, name):
        "see IBindingAware"
        clean_self=removeAllProxies(wrapped_self)
        if clean_self.subscribeOnBind:
            es=getNextService(wrapped_self, name)
            if es is not eventService: # if we really want the top-level
                # placeful event service to receive events from the
                # global event service we're going to have to
                # set something special up--something that subscribes
                # every startup...
                es.subscribe(PathSubscriber(wrapped_self))
    
    bound=ContextMethod(bound)
    
    def unbound(wrapped_self, name):
        "see IBindingAware"
        clean_self=removeAllProxies(wrapped_self)
        subscriber=PathSubscriber(wrapped_self)
        clean_self._v_unbinding=1
        for subscription in clean_self._subscriptions:
            subscribable=getAdapter(
                wrapped_self, ITraverser).traverse(subscription[0])
            subscribable.unsubscribe(subscriber)
        clean_self._subscriptions=()
        for subscriber in clean_self._subscribers:
            clean_self.__unsubscribeAllFromSelf(wrapped_self, subscriber[0])
        clean_self._v_unbinding=None

    unbound=ContextMethod(unbound)
    
    def __unsubscribeAllFromSelf(clean_self, wrapped_self, subscriber):
        """this is *not* an interface function, and should not be used
        outside of this class"""
    
        wrapped_subscriber=ContextWrapper(subscriber, wrapped_self)
        
        for subscriber_index in range(len(clean_self._subscribers)):
            sub=clean_self._subscribers[subscriber_index]
            if sub[0]==subscriber:
                ev_set=sub[1]
                break
        else:
            raise NotFoundError(subscriber)
        do_alert=ISubscriptionAware.isImplementedBy(subscriber)
        for ev_type in ev_set:
            subscriptions = clean_self._registry.get(ev_type)
            subs=subscriptions[:]
            subscriptions[:] = []
            for sub in subs:
                if sub[0] == subscriber: # deleted (not added back)
                    if do_alert:
                        wrapped_subscriber.unsubscribedFrom(
                            wrapped_self, ev_type or IEvent, sub[1])
                        # IEvent switch is to make optimization transparent
                else: # kept (added back)
                    subscriptions.append(sub)
        del clean_self._subscribers[subscriber_index]
        clean_self._registry=clean_self._registry #trigger persistence
    
    def unsubscribedFrom(wrapped_self, subscribable, event_type, filter):
        "see ISubscriptionAware"
        clean_self=removeAllProxies(wrapped_self)
        if getattr(clean_self, "_v_unbinding", None) is None:
            # we presumably have been unsubscribed from a higher-level
            # event service because that event service is unbinding
            # itself: we need to remove the higher level event service
            # from our subscriptions list and try to find another event
            # service to which to attach
            LocalSubscriptionAware.unsubscribedFrom(
                clean_self, subscribable, event_type, filter)
            clean_subscribable=removeAllProxies(subscribable)
            if IEventService.isImplementedBy(removeAllProxies(clean_subscribable)):
                context=getService(wrapped_self, "Events")
                # we do this instead of getNextService because the order
                # of unbinding and notification of unbinding is not
                # guaranteed
                while removeAllProxies(context) in (
                    clean_subscribable, clean_self): 
                    context=getNextService(context, "Events")
                # XXX as usual, we *must not* be working with a global service;
                # this probably should raise an error if service is global
                # service...
                # that leaves replacing top level event services an
                # interesting question, however
                context.subscribe(PathSubscriber(wrapped_self))
    
    unsubscribedFrom=ContextMethod(unsubscribedFrom)
            
        
