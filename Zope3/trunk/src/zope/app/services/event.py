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

$Id: event.py,v 1.23 2003/05/01 19:35:34 faassen Exp $
"""

from __future__ import generators
from zope.exceptions import NotFoundError

from zope.app.interfaces.event import IEvent, ISubscriber
from zope.app.interfaces.traversing import ITraverser
from zope.app.interfaces.services.event import ISubscriptionService
from zope.app.interfaces.services.event import IEventChannel, IEventService
from zope.app.interfaces.services.service import IBindingAware

from zope.component import getAdapter, getService, queryService
from zope.component import ComponentLookupError
from zope.app.services.servicenames import HubIds, EventPublication
from zope.app.services.servicenames import EventSubscription
from zope.app.component.nextservice import getNextService, queryNextService

from zope.proxy.context import ContextMethod, ContextSuper
from zope.proxy.introspection import removeAllProxies

from zope.app.event.subs import Subscribable, SubscriptionTracker

import logging

def getSubscriptionService(context):
    return getService(context, EventSubscription)

def subscribe(subscriber, event_type=IEvent, filter=None, context=None):
    if context is None and not isinstance(subscriber, (int, str, unicode)):
        context = subscriber
    return getSubscriptionService(context).subscribe(
        subscriber, event_type, filter)

def subscribeMany(subscriber, event_types=(IEvent,),
                  filter=None, context=None):
    if context is None and not isinstance(subscriber, (int, str, unicode)):
        context = subscriber
    subscribe = getSubscriptionService(context).subscribe
    for event_type in event_types:
        subscribe(subscriber, event_type, filter)

def unsubscribe(subscriber, event_type, filter=None, context=None):
    if context is None and not isinstance(subscriber, (int, str, unicode)):
        context = subscriber
    return getSubscriptionService(context).unsubscribe(
        subscriber, event_type, filter)

def unsubscribeAll(subscriber, event_type=IEvent, context=None):
    if context is None and not isinstance(subscriber, (int, str, unicode)):
        context = subscriber
    return getSubscriptionService(context).unsubscribeAll(
        subscriber, event_type)

def iterSubscriptions(subscriber=None, event_type=None, local_only=False,
                      context=None):
    if context is None and not isinstance(subscriber, (int, str, unicode)):
        context = subscriber
    return getSubscriptionService(context).iterSubscriptions(
        subscriber, event_type, local_only)


class EventChannel(Subscribable):

    __implements__ = IEventChannel

    # needs __init__ from zope.app.event.subs.Subscribable

    def _notify(clean_self, wrapped_self, event):
        subscriptionsForEvent = clean_self._registry.getAllForObject(event)
        hubIdsService = queryService(wrapped_self, HubIds)
        if hubIdsService is None:
            # This will only happen if there is no HubIds service.
            # This is only true at start-up, so we don't bother testing
            # whether hubGet is None in the loop below.
            hubGet = None
        else:
            hubGet = hubIdsService.getObject
        pathGet = getAdapter(wrapped_self, ITraverser).traverse

        badSubscribers = {}  # using a dict as a set
        for subscriptions in subscriptionsForEvent:
            for subscriber,filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                if isinstance(subscriber, int):
                    try:
                        obj = hubGet(subscriber)
                    except NotFoundError:
                        badSubscribers[subscriber] = None
                        continue
                else:
                    try:
                        obj = pathGet(subscriber)
                    except NotFoundError:
                        badSubscribers[subscriber] = None
                        continue
                # Get an ISubscriber adapter in the context of the object
                # This is probably the right context to use.
                #
                # Using getAdapter rather than queryAdapter because if there
                # is no ISubscriber adapter available, that is an application
                # error that should be fixed. So, failing is appropriate, and
                # adding this subscriber to badSubscribers is inappropriate.
                getAdapter(obj, ISubscriber).notify(event)

        for subscriber in badSubscribers:
            logging.getLogger('SiteError').warn(
                "Notifying a subscriber that does not exist."
                " Unsubscribing it: %s" % subscriber)
            # Also, is it right that we should sometimes have
            # "write caused by a read" semantics? I'm seeing notify() as
            # basically a read, and (un)subscribe as a write.
            wrapped_self.unsubscribeAll(subscriber)

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

    _subscribeToServiceName = EventSubscription
    _subscribeToServiceInterface = IEvent
    _subscribeToServiceFilter = None

    def subscribe(wrapped_self, reference, event_type=IEvent, filter=None):
        if getattr(wrapped_self, "_v_ssecunbinding", None) is not None:
            raise Exception(
                'Cannot subscribe to a subscriber that is unbinding.')
        return ContextSuper(ServiceSubscriberEventChannel, wrapped_self
                ).subscribe(reference, event_type, filter)
    subscribe = ContextMethod(subscribe)

    def bound(wrapped_self, name):
        "See IBindingAware"
        # Note: if a component is used for more than one service then
        # this and the unbound code must be conditional for the
        # pertinent service that should trigger event subscription
        clean_self = removeAllProxies(wrapped_self)
        clean_self._serviceName = name  # for ServiceSubscribable
        if clean_self.subscribeOnBind:
            es = queryService(wrapped_self, clean_self._subscribeToServiceName)
            if es is not None:
                if removeAllProxies(es) is clean_self:
                    es = queryNextService(
                        wrapped_self, clean_self._subscribeToServiceName)
            if es is None:
                subscribe_to = clean_self._subscribeToServiceName
                logging.getLogger('SiteError').warn(
                    "Unable to subscribe %s service to the %s service "
                    "while binding the %s service. This is because the "
                    "%s service could not be found." %
                    (name, subscribe_to, name, subscribe_to))
            else:
                es.subscribe(
                    wrapped_self,
                    clean_self._subscribeToServiceInterface,
                    clean_self._subscribeToServiceFilter
                    )
    bound = ContextMethod(bound)

    def unbound(wrapped_self, name):
        "See IBindingAware"
        # Note: if a component is used for more than one service then
        # this and the unbound code must be conditional for the
        # pertinent service that should trigger event subscription

        clean_self = removeAllProxies(wrapped_self)

        # unsubscribe all subscriptions
        hubIds = clean_self._hubIds
        unsubscribeAll = wrapped_self.unsubscribeAll
        try:
            clean_self._v_ssecunbinding = True
            while hubIds:
                hubId = iter(hubIds).next()
                unsubscribeAll(hubId, local_only=True)

            paths = clean_self._paths
            while paths:
                path = iter(paths).next()
                unsubscribeAll(path, local_only=True)
        finally:
            del clean_self._v_ssecunbinding

        assert len(paths) == len(hubIds) == len(clean_self._registry) == 0

        clean_self._serviceName = None
    unbound = ContextMethod(unbound)


class ServiceSubscribable(Subscribable):
    """A mix-in for local event services.

    * unsubscribe() asks the next higher service to unsubscribe if this
      service cannot.

    * unsubscribeAll() does the same.

    * listSubscriptions() includes this service's subscriptions, and
      those of the next higher service.
    """

    __implements__ = Subscribable.__implements__

    _serviceName = None # should be replaced; usually done in "bound"
                        # method of a subclass that is IBindingAware

    # requires __init__ from zope.app.event.subs.Subscribable

    def unsubscribe(wrapped_self, reference, event_type, filter=None):
        # The point here is that if we can't unsubscribe here, we should
        # allow the next event service to unsubscribe.
        try:
            ContextSuper(ServiceSubscribable, wrapped_self).unsubscribe(
                reference, event_type, filter)
        except NotFoundError:
            next_service = queryNextService(wrapped_self,
                                            wrapped_self._serviceName)
            if next_service is not None:
                next_service.unsubscribe(reference, event_type, filter)
            else:
                raise
    unsubscribe = ContextMethod(unsubscribe)

    def unsubscribeAll(wrapped_self, reference, event_type=IEvent,
                       local_only=False):
        # unsubscribe all from here, and from the next service

        # n is the number of subscriptions removed
        n = ContextSuper(ServiceSubscribable, wrapped_self).unsubscribeAll(
            reference, event_type)
        if not local_only:
            next_service = queryNextService(wrapped_self,
                                            wrapped_self._serviceName)
            if next_service is not None:
                n += next_service.unsubscribeAll(reference, event_type)
        return n
    unsubscribeAll = ContextMethod(unsubscribeAll)

    def resubscribeByHubId(wrapped_self, reference):
        n = ContextSuper(ServiceSubscribable, wrapped_self
            ).resubscribeByHubId(reference)
        next_service = queryNextService(wrapped_self,
                                        wrapped_self._serviceName)
        if next_service is not None:
            n += next_service.resubscribeByHubId(reference)
        return n

    def resubscribeByPath(wrapped_self, reference):
        n = ContextSuper(ServiceSubscribable, wrapped_self
            ).resubscribeByPath(reference)
        next_service = queryNextService(wrapped_self,
                                        wrapped_self._serviceName)
        if next_service is not None:
            n += next_service.resubscribeByPath(reference)
        return n

    def iterSubscriptions(wrapped_self, reference=None, event_type=IEvent,
                          local_only=False):
        'See ISubscriptionService'
        subs = ContextSuper(ServiceSubscribable, wrapped_self
                ).iterSubscriptions(reference, event_type)
        for subscription in subs:
            yield subscription

        if not local_only:
            next_service = queryNextService(wrapped_self,
                                            wrapped_self._serviceName)
            if next_service is not None:
                for subscription in next_service.iterSubscriptions(
                    reference, event_type):
                    yield subscription
    iterSubscriptions = ContextMethod(iterSubscriptions)


from zope.app.interfaces.services.service import ISimpleService

class EventService(ServiceSubscriberEventChannel, ServiceSubscribable):

    __implements__ = (
        IEventService,
        ISubscriptionService,
        ISimpleService,
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

        publishedEvents = getattr(clean_self, "_v_publishedEvents", [])
        clean_self._v_publishedEvents = publishedEvents
        publishedEvents.append(event)
        try:
            clean_self._notify(wrapped_self, event)
            if clean_self.isPromotableEvent(event):
                getNextService(wrapped_self, EventPublication).publish(event)
        finally:
            publishedEvents.remove(event)
    publish = ContextMethod(publish)

    def notify(wrapped_self, event):
        "see ISubscriber"
        clean_self = removeAllProxies(wrapped_self)
        publishedEvents = getattr(clean_self, "_v_publishedEvents", [])
        if event not in publishedEvents:
            clean_self._notify(wrapped_self, event)
    notify = ContextMethod(notify)

    def bound(wrapped_self, name):
        "See IBindingAware"
        # An event service is bound as EventSubscription and EventPublication.
        # We only want to subscribe to the next event service when we're bound
        # as EventSubscription
        if name == EventSubscription:
            clean_self = removeAllProxies(wrapped_self)
            clean_self._serviceName = name  # for ServiceSubscribable
            if clean_self.subscribeOnBind:
                try:
                    es = getNextService(wrapped_self, EventSubscription)
                except ComponentLookupError:
                    pass
                else:
                    es.subscribe(wrapped_self)
    bound = ContextMethod(bound)

    def unbound(wrapped_self, name):
        "See IBindingAware"
        # An event service is bound as EventSubscription and EventPublication.
        # We only want to unsubscribe from the next event service when
        # we're unbound as EventSubscription
        if name == EventSubscription:
            clean_self = removeAllProxies(wrapped_self)
            clean_self._v_unbinding = True
            try:
                ContextSuper(EventService, wrapped_self).unbound(name)

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
            # end copy/paste
            finally:
                # unset flag
                del clean_self._v_unbinding
    unbound = ContextMethod(unbound)

    def unsubscribedFrom(wrapped_self, subscribable, event_type, filter):
        "See ISubscribingAware"
        ContextSuper(EventService, wrapped_self).unsubscribedFrom(
            subscribable, event_type, filter)
        clean_self = removeAllProxies(wrapped_self)
        if getattr(clean_self, "_v_unbinding", None) is None:
            # we presumably have been unsubscribed from a higher-level
            # event service because that event service is unbinding
            # itself: we need to remove the higher level event service
            # from our subscriptions list and try to find another event
            # service to which to attach
            clean_subscribable = removeAllProxies(subscribable)
            if ISubscriptionService.isImplementedBy(
                removeAllProxies(clean_subscribable)):
                try:
                    context = getService(wrapped_self, EventSubscription)
                    # we do this instead of getNextService because the order
                    # of unbinding and notification of unbinding is not
                    # guaranteed
                    while removeAllProxies(context) in (
                        clean_subscribable, clean_self): 
                        context = getNextService(context, EventSubscription)
                except ComponentLookupError:
                    pass
                else:
                    context.subscribe(wrapped_self)
    unsubscribedFrom = ContextMethod(unsubscribedFrom)

