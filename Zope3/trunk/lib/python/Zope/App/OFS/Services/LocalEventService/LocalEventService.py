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
$Id: LocalEventService.py,v 1.11 2002/12/12 20:05:51 jack-e Exp $
"""

from Zope.Event.GlobalEventService import eventService
from Zope.Event.IEvent import IEvent
from Zope.Event.IEventService import IEventService
from Zope.Event.ISubscriptionAware import ISubscriptionAware
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.App.Traversing import traverse
from Zope.ComponentArchitecture import getAdapter, getService
from Zope.App.ComponentArchitecture.NextService import getNextService
from Zope.ContextWrapper import ContextMethod
from Zope.Exceptions import NotFoundError
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Proxy.ProxyIntrospection import removeAllProxies



from ProtoServiceEventChannel import ProtoServiceEventChannel

class LocalEventService(ProtoServiceEventChannel):
        
    __implements__ = (
        IEventService,
        ProtoServiceEventChannel.__implements__
        )
    
    # uses (and needs) __init__ from base class
    
    def isPromotableEvent(self, event):
        """a hook.  Returns a true value if, when publishing an
        event, the event should also be promoted to the
        next (higher) level of event service, and a false value
        otherwise."""
        # XXX A probably temporary appendage.  Depending on the usage,
        # this should be (a) kept as is, (b) made into a registry, or
        # (c) removed.
        return 1
    
    def publish(wrapped_self, event):
        "see IEventService"
        clean_self = removeAllProxies(wrapped_self)
        
        subscriptionses = clean_self._registry.getAllForObject(event)

        for subscriptions in subscriptionses:
            # for subscriber_path, filter in subscriptions:
            for subscriber_path,filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                # XXX resolve subscriber_path
                traverse(wrapped_self, subscriber_path).notify(event)

        publishedEvents = getattr(clean_self, "_v_publishedEvents", None)
        if publishedEvents is None:
            publishedEvents = clean_self._v_publishedEvents=[event]
        else:
            publishedEvents.append(event)
        if(clean_self.isPromotableEvent(event)):
            getNextService(wrapped_self, 'Events').publish(event)
        publishedEvents.remove(event)
    publish = ContextMethod(publish)
        
    def notify(wrapped_self, event):
        "see ISubscriber"
        clean_self = removeAllProxies(wrapped_self)
        publishedEvents = getattr(clean_self, "_v_publishedEvents", None)
        if publishedEvents is None or event not in publishedEvents:
            subscriptionses = clean_self._registry.getAllForObject(event)

            for subscriptions in subscriptionses:
                # for subscriber_path, filter in subscriptions:
                for subscriber_path, filter in subscriptions:
                    if filter is not None and not filter(event):
                        continue
                    # XXX resolve subscriber_path
                    traverse(wrapped_self, subscriber_path).notify(event)
    notify = ContextMethod(notify)
    
    def bound(wrapped_self, name):
        "see IBindingAware"
        clean_self = removeAllProxies(wrapped_self)
        clean_self._serviceName = name # for LocalServiceSubscribable
        if clean_self.subscribeOnBind:
            es = getNextService(wrapped_self, "Events")
            if es is not eventService:
                # XXX if we really want to receive events from the
                # global event service we're going to have to
                # set something special up--something that subscribes
                # every startup...
                # XXX just pass wrapped_self
                es.subscribe(wrapped_self)
    bound = ContextMethod(bound)
    
    # _unbound = ProtoServiceEventChannel.unbound # see comment below
    
    def unbound(wrapped_self, name):
        "see IBindingAware"
        clean_self = removeAllProxies(wrapped_self)
        clean_self._v_unbinding = True
        # this flag is used by the unsubscribedFrom method (below) to
        # determine that it doesn't need to further unsubscribe beyond
        # what we're already doing.
        
        # Both of the following approaches have wrapper/security
        # problems:
        #
        #  wrapped_self._unbound(name) # using _unbound above
        # and
        #  ProtoServiceEventChannel.unbound(wrapped_self, name)
        #
        # so we're doing a copy and paste from ProtoServiceEventChannel:
        # start copy/paste
        # XXX subscriber = wrapped_self
        for subscription in clean_self._subscriptions:
            subscribable = getAdapter(
                wrapped_self, ITraverser).traverse(subscription[0])
            subscribable.unsubscribe(wrapped_self)
        clean_self._subscriptions = ()
        clean_self._serviceName = None
        # end copy/paste
        
        # ambigous name subscriber -> (subscriber_path, filter, )
        for subscriber in clean_self._subscribers:
            clean_self.__unsubscribeAllFromSelf(wrapped_self, subscriber[0])
        # unset flag
        clean_self._v_unbinding = None
    unbound = ContextMethod(unbound)
    
    # XXX gets subscriber_path as last argument
    def __unsubscribeAllFromSelf(clean_self, wrapped_self, subscriber_path):
        """this is *not* an interface function, and should not be used
        outside of this class"""
        
        # XXX resolve subscriber from path first
        subscriber = traverse(wrapped_self, subscriber_path)
        
        for subscriber_index in range(len(clean_self._subscribers)):
            sub = clean_self._subscribers[subscriber_index]
            # XXX subscriber_path
            if sub[0] == subscriber_path:
                ev_set = sub[1]
                break
        else:
            raise NotFoundError(subscriber)
        clean_self._p_changed = 1 # trigger persistence before change
        do_alert = ISubscriptionAware.isImplementedBy(subscriber)
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
                        # IEvent switch is to make optimization transparent
                else: # kept (added back)
                    subscriptions.append(sub)
        del clean_self._subscribers[subscriber_index]
    
    def unsubscribedFrom(wrapped_self, subscribable, event_type, filter):
        "see ISubscriptionAware"
        clean_self = removeAllProxies(wrapped_self)
        if getattr(clean_self, "_v_unbinding", None) is None:
            # we presumably have been unsubscribed from a higher-level
            # event service because that event service is unbinding
            # itself: we need to remove the higher level event service
            # from our subscriptions list and try to find another event
            # service to which to attach
            ProtoServiceEventChannel.unsubscribedFrom(
                clean_self, subscribable, event_type, filter)
            clean_subscribable = removeAllProxies(subscribable)
            if IEventService.isImplementedBy(
                removeAllProxies(clean_subscribable)):
                context = getService(wrapped_self, "Events")
                # we do this instead of getNextService because the order
                # of unbinding and notification of unbinding is not
                # guaranteed
                while removeAllProxies(context) in (
                    clean_subscribable, clean_self): 
                    context = getNextService(context, "Events")
                # XXX as usual, we *must not* be working with a global service;
                # this probably should raise an error if service is global
                # service...
                # that leaves replacing top level event services an
                # interesting question, however
                
                # XXX just pass wrapped_self
                context.subscribe(wrapped_self)
    unsubscribedFrom = ContextMethod(unsubscribedFrom)

