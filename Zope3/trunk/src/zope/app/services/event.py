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
"""Event service implementation.

$Id: event.py,v 1.2 2002/12/25 14:13:19 jim Exp $
"""

from persistence import Persistent

from zope.app.component.nextservice import getNextService
from zope.app.event.globaleventservice import eventService
from zope.app.interfaces.services.event import IPathSubscriber
from zope.app.interfaces.traversing.traverser import ITraverser
from zope.app.traversing import getPhysicalPathString
from zope.component import getAdapter
from zope.component import getService
from zope.event.subscribable import Subscribable
from zope.exceptions import NotFoundError
from zope.interface import Attribute
from zope.interfaces.event import IEvent
from zope.interfaces.event import IEventChannel
from zope.interfaces.event import IEventService
from zope.interfaces.event import ISubscriptionAware
from zope.proxy.context import ContextWrapper
from zope.proxy.context import isWrapper
from zope.proxy.context import ContextMethod
from zope.proxy.introspection import removeAllProxies

from zope.app.component.nextservice import getNextService, queryNextService
from zope.app.interfaces.services.service import IBindingAware
from zope.app.traversing import getPhysicalPathString, traverse


class LocalSubscribable(Persistent, Subscribable):
    """a local mix-in"""

    __implements__ = (
        Subscribable.__implements__,
        Persistent.__implements__)

    # uses (and needs) __init__ from zope.event.subscribable

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
        # XXX should this and similar be done earlier in the method?
        # XXX Ask Shane


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
        # XXX should be done earlier?  Ask Shane

    unsubscribe = ContextMethod(unsubscribe)


class LocalServiceSubscribable(LocalSubscribable):
    """a local mix-in for services"""

    __implements__ = LocalSubscribable.__implements__

    _serviceName = None # should be replaced; usually done in "bound"
                        # method of a subclass

    # uses (and needs) __init__ from zope.event.subscribable (via
    # localsubscribable)

    def unsubscribe(wrapped_self,
                    subscriber,
                    event_type=None,
                    filter=None):
        # might be wrapped, might not
        subscriber = removeAllProxies(subscriber)

        clean_self = removeAllProxies(wrapped_self)
        wrapped_subscriber = ContextWrapper(subscriber, wrapped_self)

        for subscriber_index in range(len(clean_self._subscribers)):
            sub = clean_self._subscribers[subscriber_index]
            if sub[0] == subscriber:
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
            # we have to clean all the event types out (ignoring filter)
            for ev_type in ev_set:
                subscriptions = clean_self._registry.get(ev_type)
                subs = subscriptions[:]
                subscriptions[:] = []
                for sub in subs:
                    if sub[0] == subscriber: # deleted (not added back)
                        if do_alert:
                            wrapped_subscriber.unsubscribedFrom(
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
        # might be wrapped, might not
        subscriber = removeAllProxies(subscriber)

        clean_self = removeAllProxies(wrapped_self)
        result = LocalSubscribable.listSubscriptions(
            clean_self, subscriber, event_type)
        next_service = queryNextService(wrapped_self, clean_self._serviceName)
        if next_service is not None:
            result.extend(next_service.listSubscriptions(subscriber,
                                                         event_type))
        return result
    listSubscriptions = ContextMethod(listSubscriptions)


class LocalEventChannel(LocalSubscribable):

    __implements__ = IEventChannel

    # needs __init__ from zope.event.subscribable (via
    # localsubscribable)!!

    def notify(wrapped_self, event):
        clean_self = removeAllProxies(wrapped_self)

        subscriptionses = clean_self.subscriptionsForEvent(event)
        # that's a non-interface shortcut for
        # subscriptionses = clean_self._registry.getAllForObject(event)

        for subscriptions in subscriptionses:
            for subscriber,filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                ContextWrapper(subscriber, wrapped_self).notify(event)
    notify = ContextMethod(notify)


class LocalSubscriptionAware:
    "mix-in for subscribers that want to know to whom they are subscribed"

    __implements__ = ISubscriptionAware

    def __init__(self):
        self._subscriptions = ()

    def subscribedTo(self, subscribable, event_type, filter):
        # This breaks for subscriptions to global event service.
        # Unless the global event service becomes persistent, this
        # is probably correct behavior.
        subscribable_path = getPhysicalPathString(subscribable)
        if (subscribable_path, event_type, filter) not in self._subscriptions:
            self._subscriptions += ((subscribable_path, event_type, filter),)

    def unsubscribedFrom(self, subscribable, event_type, filter):
        # global event service breaks, as above
        subscribable_path = getPhysicalPathString(subscribable)
        sub = list(self._subscriptions)
        sub.remove((subscribable_path, event_type, filter))
        self._subscriptions = tuple(sub)


class ProtoServiceEventChannel(
    LocalSubscriptionAware,
    LocalServiceSubscribable,
    LocalEventChannel):
    """An event channel that wants to subscribe to the nearest
    event service when bound, and unsubscribe when unbound, as one
    needs for an event channel that will be a service"""

    __implements__ = (
        LocalEventChannel.__implements__,
        LocalServiceSubscribable.__implements__,
        LocalSubscriptionAware.__implements__,
        IBindingAware
        )

    def __init__(self):
        LocalServiceSubscribable.__init__(self)
        LocalSubscriptionAware.__init__(self)

    subscribeOnBind = True
        # if true, event service will subscribe
        # to the parent event service on binding, unless the parent
        # service is the global event service; see 'bound' method
        # below

    _serviceName = None
        # the name of the service that this object is providing, or
        # None if unbound

    _subscribeToServiceName = "Events"
    _subscribeToServiceInterface = IEvent
    _subscribeToServiceFilter = None

    def bound(wrapped_self, name):
        "see IBindingAware"
        clean_self = removeAllProxies(wrapped_self)
        clean_self._serviceName = name # for LocalServiceSubscribable
        if clean_self.subscribeOnBind:
            es = getService(wrapped_self, clean_self._subscribeToServiceName)
            if isWrapper(es):
                # if we really want to receive events from a
                # global event-type service we're going to have to
                # set something special up -- something that subscribes
                # every startup...
                es.subscribe(
                    PathSubscriber(wrapped_self),
                    clean_self._subscribeToServiceInterface,
                    clean_self._subscribeToServiceFilter
                    )

    bound = ContextMethod(bound)

    def unbound(wrapped_self, name):
        "see IBindingAware"
        clean_self = removeAllProxies(wrapped_self)
        subscriber = PathSubscriber(wrapped_self)
        for subscription in clean_self._subscriptions:
            subscribable = getAdapter(
                wrapped_self, ITraverser).traverse(subscription[0])
            subscribable.unsubscribe(subscriber)
        clean_self._subscriptions = ()
        clean_self._serviceName = None

    unbound = ContextMethod(unbound)


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
            for subscriber,filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                ContextWrapper(subscriber, wrapped_self).notify(event)

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
                for subscriber,filter in subscriptions:
                    if filter is not None and not filter(event):
                        continue
                    ContextWrapper(subscriber, wrapped_self).notify(event)
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
                es.subscribe(PathSubscriber(wrapped_self))
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
        subscriber = PathSubscriber(wrapped_self)
        for subscription in clean_self._subscriptions:
            subscribable = getAdapter(
                wrapped_self, ITraverser).traverse(subscription[0])
            subscribable.unsubscribe(subscriber)
        clean_self._subscriptions = ()
        clean_self._serviceName = None
        # end copy/paste

        for subscriber in clean_self._subscribers:
            clean_self.__unsubscribeAllFromSelf(wrapped_self, subscriber[0])
        # unset flag
        clean_self._v_unbinding = None
    unbound = ContextMethod(unbound)

    def __unsubscribeAllFromSelf(clean_self, wrapped_self, subscriber):
        """this is *not* an interface function, and should not be used
        outside of this class"""
        wrapped_subscriber = ContextWrapper(subscriber, wrapped_self)

        for subscriber_index in range(len(clean_self._subscribers)):
            sub = clean_self._subscribers[subscriber_index]
            if sub[0] == subscriber:
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
                if sub[0] == subscriber: # deleted (not added back)
                    if do_alert:
                        wrapped_subscriber.unsubscribedFrom(
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
                context.subscribe(PathSubscriber(wrapped_self))
    unsubscribedFrom = ContextMethod(unsubscribedFrom)


class AbstractIndirectSubscriber:

    def notify(wrapped_self, event):
        removeAllProxies(wrapped_self)._getSubscriber(
            wrapped_self).notify(event)

    notify=ContextMethod(notify)

    def subscribedTo(wrapped_self, subscribable, event_type, filter):
        proxiedObj = removeAllProxies(
            wrapped_self)._getSubscriber(wrapped_self)
        if ISubscriptionAware.isImplementedBy(
            removeAllProxies(proxiedObj)):
            proxiedObj.subscribedTo(
                subscribable, event_type, filter )

    subscribedTo=ContextMethod(subscribedTo)

    def unsubscribedFrom(wrapped_self, subscribable, event_type, filter):
        proxiedObj = removeAllProxies(
            wrapped_self)._getSubscriber(wrapped_self)
        if ISubscriptionAware.isImplementedBy(
            removeAllProxies(proxiedObj)):
            proxiedObj.unsubscribedFrom(
                subscribable, event_type, filter )

    unsubscribedFrom=ContextMethod(unsubscribedFrom)


class PathSubscriber(AbstractIndirectSubscriber):

    __implements__ = IPathSubscriber, ISubscriptionAware

    def __init__(self, wrapped_subscriber):
        self.subscriber_path = getPhysicalPathString(wrapped_subscriber)

    def __eq__(self, other):
        return (IPathSubscriber.isImplementedBy(other) and
               other.subscriber_path == self.subscriber_path)

    def _getSubscriber(self, wrapped_self):
        return traverse(wrapped_self, self.subscriber_path)
