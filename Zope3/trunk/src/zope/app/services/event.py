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
"""Local Event Service and related classes.

$Id: event.py,v 1.6 2002/12/30 14:04:45 stevea Exp $
"""

from zope.exceptions import NotFoundError

from zope.app.interfaces.event import ISubscribingAware, IPublisher, IEvent
from zope.app.interfaces.traversing import ITraverser
from zope.app.interfaces.services.event import ISubscriptionService
from zope.app.interfaces.services.event import IEventChannel, IEventService
from zope.app.interfaces.services.service import IBindingAware

from zope.component import getAdapter, getService, queryService
from zope.component import ComponentLookupError
from zope.app.component.nextservice import getNextService, queryNextService

from zope.proxy.context import ContextMethod
from zope.proxy.introspection import removeAllProxies

from zope.app.event.subs import Subscribable, SubscriptionTracker


def getSubscriptionService(context):
    return getService(context, "Subscription")

def subscribe(subscriber, event_type=IEvent, filter=None, context=None):
    if context is None:
        context = subscriber
    return getSubscriptionService(context).subscribe(
        subscriber, event_type, filter)

def subscribeMany(subscriber, event_types=(IEvent,),
                  filter=None, context=None):
    if context is None:
        context = subscriber
    subscribe = getSubscriptionService(context).subscribe
    for event_type in event_types:
        subscribe(subscriber, event_type, filter)

def unsubscribe(subscriber, event_type=None, filter=None, context=None):
    if context is None:
        context = subscriber
    return getSubscriptionService(context).unsubscribe(
        subscriber, event_type, filter)

def listSubscriptions(subscriber, event_type=None, context=None):
    if context is None:
        context = subscriber
    return getSubscriptionService(context).listSubscriptions(
        subscriber, event_type)


class EventChannel(Subscribable):
    
    __implements__ = IEventChannel
    
    # needs __init__ from zope.app.event.subs.Subscribable
    
    def _notify(clean_self, wrapped_self, event):
        subscriptionsForEvent = clean_self._registry.getAllForObject(event) 
        hubGet = getService(wrapped_self, "HubIds").getObject
        pathGet = getAdapter(wrapped_self, ITraverser).traverse
        
        badSubscribers = {}
        
        for subscriptions in subscriptionsForEvent:
            for subscriber,filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                if isinstance(subscriber, int):
                    try:
                        obj = hubGet(subscriber)
                    except NotFoundError:
                        badSubscribers[subscriber] = 1
                        continue
                else:
                    try:
                        obj = pathGet(subscriber)
                    except NotFoundError:
                        badSubscribers[subscriber] = 1
                        continue
                obj.notify(event)
        
        for subscriber in badSubscribers.keys():
            clean_self.unsubscribe(subscriber)
        
        
    def notify(wrapped_self, event):
        clean_self = removeAllProxies(wrapped_self)
        clean_self._notify(wrapped_self, event)
    notify = ContextMethod(notify)


class ServiceSubscriberEventChannel(SubscriptionTracker, EventChannel):
    """An event channel that wants to subscribe to the nearest
    event service when bound, and unsubscribe when unbound.
    """
    
    __implements__ = (
        EventChannel.__implements__,
        SubscriptionTracker.__implements__,
        IBindingAware
        )
   
    def __init__(self):
        SubscriptionTracker.__init__(self)
        EventChannel.__init__(self)
    
    subscribeOnBind = True
        # if true, event service will subscribe
        # to the parent event service on binding, unless the parent
        # service is the global event service; see 'bound' method
        # below
    
    _serviceName = None
        # the name of the service that this object is providing, or
        # None if unbound
    
    _subscribeToServiceName = "Subscriptions"
    _subscribeToServiceInterface = IEvent
    _subscribeToServiceFilter = None
    
    def bound(wrapped_self, name):
        "See IBindingAware"
        # Note: if a component is used for more than one service then
        # this and the unbound code must be conditional for the
        # pertinent service that should trigger event subscription
        clean_self = removeAllProxies(wrapped_self)
        clean_self._serviceName = name # for LocalServiceSubscribable
        if clean_self.subscribeOnBind:
            es = queryService(wrapped_self, clean_self._subscribeToServiceName)
            if es is not None:
                es.subscribe(
                    wrapped_self,
                    clean_self._subscribeToServiceInterface,
                    clean_self._subscribeToServiceFilter
                    )
    bound = ContextMethod(bound)
    
    def unbound(wrapped_self, name):
        "See IBindingAware"
        # see comment in "bound" above
        clean_self = removeAllProxies(wrapped_self)
        getPath = getAdapter(wrapped_self, ITraverser).traverse
        for subscription in clean_self._subscriptions:
            subscribable = getPath(subscription[0])
            subscribable.unsubscribe(wrapped_self)
        clean_self._subscriptions = ()
        clean_self._serviceName = None
    unbound = ContextMethod(unbound)



class ServiceSubscribable(Subscribable):
    """A mix-in for local event services.
    
    * unsubscribe() asks the next higher service to unsubscribe if this
      service cannot.

    * listSubscriptions() includes this service's subscriptions, and
      those of the next higher service.
    """
    
    __implements__ = Subscribable.__implements__
    
    _serviceName = None # should be replaced; usually done in "bound"
                        # method of a subclass that is IBindingAware
    
    # uses (and needs) __init__ from zope.app.event.subs.Subscribable
    
    def unsubscribe(wrapped_self, subscriber, event_type=None, filter=None):
        originalSubscriber = subscriber
        clean_self = removeAllProxies(wrapped_self)
        subscribers, clean_subObj, subObj = clean_self._getSubscribers(
            wrapped_self, subscriber)
        
        try:
            ev_sets = clean_self._getEventSets(subscribers)
        except NotFoundError:
            next_service = queryNextService(wrapped_self,
                                            clean_self._serviceName)
            if next_service is not None:
                next_service.unsubscribe(originalSubscriber,
                                         event_type,
                                         filter)
            elif event_type is not None:
                raise NotFoundError(originalSubscriber,
                                    event_type,
                                    filter)
            return
        
        do_alert = (subObj is not None and
                    ISubscribingAware.isImplementedBy(clean_subObj))
        
        clean_self._p_changed = 1
        
        if event_type is not None:
            # we have to clean out one and only one subscription of this
            # subscriber for event_type, filter (there may be more, even for
            # this exact combination of subscriber, event_type, filter; we
            # only delete *one*)
            ev_type = event_type

            # *** handle optimization: a subscription to IEvent is a
            # subscription to all events; this is converted to 'None' so
            # that the _registry can shortcut some of its tests
            if event_type is IEvent:
                ev_type = None
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
                                    else: # len(ev_set) == 1
                                        del clean_self._subscribers[
                                            subscriber_index]
                            break
            else:
                next_service = queryNextService(wrapped_self,
                                                clean_self._serviceName)
                if next_service is not None:
                    next_service.unsubscribe(originalSubscriber,
                                             event_type,
                                             filter)
                else:
                    raise NotFoundError(originalSubscriber, event_type, filter)
        else:
            # we have to clean all the event types out (ignoring filter)
            clean_self._cleanAllForSubscriber(wrapped_self,
                                              ev_sets,
                                              do_alert,
                                              subObj)
            next_service = queryNextService(wrapped_self,
                                            clean_self._serviceName)
            if next_service is not None:
                next_service.unsubscribe(originalSubscriber,
                                         event_type,
                                         filter)
    unsubscribe = ContextMethod(unsubscribe)

    def listSubscriptions(wrapped_self, subscriber, event_type=None):
        clean_self = removeAllProxies(wrapped_self)
        subscribers, clean_subObj, subObj = clean_self._getSubscribers(
            wrapped_self, subscriber)
        
        result=[]
        if event_type:
            ev_type = event_type
            if event_type is IEvent:
                ev_type = None # handle optimization
            subscriptions = clean_self._registry.get(ev_type)
            if subscriptions:
                for sub in subscriptions:
                    for subscriber in subscribers:
                        if sub[0] == subscriber:
                            result.append((event_type, sub[1]))
        else:
            try:
                ev_sets = clean_self._getEventSets(subscribers)
            except NotFoundError:
                return result
            for (subscriber, subscriber_index), ev_set in ev_sets.items():
                for ev_type in ev_set:
                    subscriptions = clean_self._registry.get(ev_type)
                    if subscriptions:
                        if ev_type is None:
                            ev_type = IEvent
                        for sub in subscriptions:
                            if sub[0] == subscriber:
                                result.append((ev_type, sub[1]))
        next_service = queryNextService(wrapped_self, clean_self._serviceName)
        if next_service is not None:
            result.extend(
                    next_service.listSubscriptions(subscriber, event_type)
                    )
        return result
    listSubscriptions = ContextMethod(listSubscriptions)



class EventService(ServiceSubscriberEventChannel, ServiceSubscribable):
        
    __implements__ = (
        IEventService,
        ServiceSubscribable.__implements__,
        ServiceSubscriberEventChannel.__implements__
        )
    
    def __init__(self):
        ServiceSubscriberEventChannel.__init__(self)
        ServiceSubscribable.__init__(self)
        
    def isPromotableEvent(self, event):
        """A hook.  Returns True if, when publishing an event, the event
        should also be promoted to the next (higher) level of event service,
        and False otherwise."""
        # XXX A probably temporary appendage.  Depending on the usage,
        # this should be (a) kept as is, (b) made into a registry, or
        # (c) removed.
        return True
    
    def publish(wrapped_self, event):
        "see IEventPublisher"
        clean_self = removeAllProxies(wrapped_self)
        clean_self._notify(wrapped_self, event)

        publishedEvents = getattr(clean_self, "_v_publishedEvents", None)
        if publishedEvents is None:
            publishedEvents = clean_self._v_publishedEvents=[event]
        else:
            publishedEvents.append(event)
        if (clean_self.isPromotableEvent(event)):
            getNextService(wrapped_self, 'Events').publish(event)
        publishedEvents.remove(event)
    publish = ContextMethod(publish)
        
    def notify(wrapped_self, event):
        "see ISubscriber"
        clean_self = removeAllProxies(wrapped_self)
        publishedEvents = getattr(clean_self, "_v_publishedEvents", None)
        if publishedEvents is None or event not in publishedEvents:
            clean_self._notify(wrapped_self, event)
    notify = ContextMethod(notify)
    
    def bound(wrapped_self, name):
        "See IBindingAware"
        if name == "Subscription":
            clean_self = removeAllProxies(wrapped_self)
            clean_self._serviceName = name # for LocalServiceSubscribable
            if clean_self.subscribeOnBind:
                try:
                    es = getNextService(wrapped_self, "Subscription")
                except ComponentLookupError:
                    pass
                else:
                    es.subscribe(wrapped_self)
    bound = ContextMethod(bound)
    
    # _unbound = ServiceSubscriberEventChannel.unbound # see comment below
    
    def unbound(wrapped_self, name):
        "See IBindingAware"
        if name == "Subscription":
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
            #  ServiceSubscriberEventChannel.unbound(wrapped_self, name)
            #
            # so we're doing a copy and paste from
            # ServiceSubscriberEventChannel:
            # 
            # start copy/paste
            getPath = getAdapter(wrapped_self, ITraverser).traverse
            for subscription in clean_self._subscriptions:
                subscribable = getPath(subscription[0])
                subscribable.unsubscribe(wrapped_self)
            clean_self._subscriptions = ()
            clean_self._serviceName = None
            # end copy/paste
            
            for subscriber in clean_self._subscribers:
                clean_self.__unsubscribeAllFromSelf(
                        wrapped_self, subscriber[0])
            # unset flag
            clean_self._v_unbinding = None
    unbound = ContextMethod(unbound)
    
    def __unsubscribeAllFromSelf(clean_self, wrapped_self, subscriber):
        subscribers, clean_subObj, subObj = clean_self._getSubscribers(
            wrapped_self, subscriber)
        ev_sets = clean_self._getEventSets(subscribers)
        do_alert = (subObj is not None and
                    ISubscribingAware.isImplementedBy(clean_subObj))
        clean_self._p_changed = 1  # trigger persistence before change
        clean_self._cleanAllForSubscriber(wrapped_self,
                                          ev_sets,
                                          do_alert,
                                          subObj)
    
    def unsubscribedFrom(wrapped_self, subscribable, event_type, filter):
        "See ISubscribingAware"
        clean_self = removeAllProxies(wrapped_self)
        if getattr(clean_self, "_v_unbinding", None) is None:
            # we presumably have been unsubscribed from a higher-level
            # event service because that event service is unbinding
            # itself: we need to remove the higher level event service
            # from our subscriptions list and try to find another event
            # service to which to attach
            ServiceSubscriberEventChannel.unsubscribedFrom(
                clean_self, subscribable, event_type, filter)
            clean_subscribable = removeAllProxies(subscribable)
            if ISubscriptionService.isImplementedBy(
                removeAllProxies(clean_subscribable)):
                try:
                    context = getService(wrapped_self, "Subscription")
                    # we do this instead of getNextService because the order
                    # of unbinding and notification of unbinding is not
                    # guaranteed
                    while removeAllProxies(context) in (
                        clean_subscribable, clean_self): 
                        context = getNextService(context, "Subscription")
                except ComponentLookupError:
                    pass
                else:
                    context.subscribe(wrapped_self)
    unsubscribedFrom = ContextMethod(unsubscribedFrom)

