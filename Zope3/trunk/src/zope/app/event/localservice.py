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

$Id$
"""
import logging
from zope.exceptions import NotFoundError

from zope.app import zapi

from zope.component import queryService
from zope.app.event.interfaces import IEvent, ISubscriber, IEventChannel
from zope.app.event.interfaces import ISubscriptionService, IEventService
from zope.app.site.interfaces import IBindingAware

from zope.component import ComponentLookupError
from zope.app.servicenames import HubIds, EventPublication, EventSubscription
from zope.app.component.localservice import getNextService, queryNextService

from zope.proxy import removeAllProxies
from zope.interface import implements

from zope.app.event.subs import Subscribable, SubscriptionTracker

from zope.security.proxy import trustedRemoveSecurityProxy
from zope.app.container.contained import Contained


def getSubscriptionService(context):
    return zapi.getService(context, EventSubscription)

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

def unsubscribeAll(subscriber, event_type=IEvent, context=None,
                   local_only=False):
    if context is None and not isinstance(subscriber, (int, str, unicode)):
        context = subscriber
    return getSubscriptionService(context).unsubscribeAll(
        subscriber, event_type, local_only=local_only)

def iterSubscriptions(subscriber=None, event_type=None, local_only=False,
                      context=None):
    if context is None and not isinstance(subscriber, (int, str, unicode)):
        context = subscriber
    return getSubscriptionService(context).iterSubscriptions(
        subscriber, event_type, local_only)


class EventChannel(Subscribable):

    implements(IEventChannel)

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

        root = removeAllProxies(zapi.getRoot(wrapped_self))

        badSubscribers = {}  # using a dict as a set
        for subscriptions in subscriptionsForEvent:
            for subscriber,filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                if isinstance(subscriber, int):
                    try:
                        obj = hubGet(subscriber)

                        # XXX we need to figure out exactly how we want to
                        # handle this. For now, we'll assume that all
                        # subscriptions are trusted, so can always notify
                        obj = trustedRemoveSecurityProxy(obj)
                    except NotFoundError:
                        badSubscribers[subscriber] = None
                        continue
                else:
                    try:
                        obj = zapi.traverse(root, subscriber)
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
                ISubscriber(obj).notify(event)

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


class ServiceSubscriberEventChannel(SubscriptionTracker, EventChannel):
    """An event channel that wants to subscribe to the nearest
    event service when bound, and unsubscribe when unbound.
    """

    implements(IBindingAware)

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

    def subscribe(self, reference, event_type=IEvent, filter=None):
        if getattr(self, "_v_ssecunbinding", None) is not None:
            raise Exception(
                'Cannot subscribe to a subscriber that is unbinding.')
        return super(ServiceSubscriberEventChannel, self
                     ).subscribe(reference, event_type, filter)

    def bound(wrapped_self, name):
        "See IBindingAware"
        # Note: if a component is used for more than one service then
        # this and the unbound code must be conditional for the
        # pertinent service that should trigger event subscription
        clean_self = removeAllProxies(wrapped_self)
        clean_self._serviceName = name  # for ServiceSubscribable
        if clean_self.subscribeOnBind:
            es = queryService(
                wrapped_self, clean_self._subscribeToServiceName)
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

    def unbound(wrapped_self, name):
        "See IBindingAware"
        # Note: if a component is used for more than one service then
        # this and the unbound code must be conditional for the
        # pertinent service that should trigger event subscription

        clean_self = removeAllProxies(wrapped_self)

        # unsubscribe all subscriptions
        hubIds = clean_self._hubIds
        unsubscribeAll = wrapped_self.unsubscribeAll

        # XXX Temporary hack to make unsubscriptions local in scope when
        #     this mix-in is used as part of a subscriptions service.
        #     The dependences of these mixins need to be documented and
        #     reevaluated.
        if ISubscriptionService.providedBy(wrapped_self):
            real_unsubscribeAll = unsubscribeAll
            unsubscribeAll = lambda x: real_unsubscribeAll(x, local_only=True)

        try:
            clean_self._v_ssecunbinding = True
            while hubIds:
                hubId = iter(hubIds).next()
                # XXX This code path needs a unit test!
                #     This code is also wrong.
                #     The call to unsubscribeAll assumes that whatever class
                #     mixes this class in provides an unsubscribeAll method
                #     that correctly uses the self._subscribeToServiceName
                #     to decide what it should be unsubscribing from.
                #     This could be any service that implements
                #     ISubscriptionService
                unsubscribeAll(hubId)

            paths = clean_self._paths
            while paths:
                path = iter(paths).next()
                # XXX This code path needs a unit test!
                #     Also, see comment above.
                unsubscribeAll(path)
        finally:
            del clean_self._v_ssecunbinding

        assert len(paths) == len(hubIds) == len(clean_self._registry) == 0

        clean_self._serviceName = None


class ServiceSubscribable(Subscribable):
    """A mix-in for local event services.

    * unsubscribe() asks the next higher service to unsubscribe if this
      service cannot.

    * unsubscribeAll() does the same.

    * listSubscriptions() includes this service's subscriptions, and
      those of the next higher service.
    """

    _serviceName = None # should be replaced; usually done in "bound"
                        # method of a subclass that is IBindingAware

    # requires __init__ from zope.app.event.subs.Subscribable

    def unsubscribe(self, reference, event_type, filter=None):
        # The point here is that if we can't unsubscribe here, we should
        # allow the next event service to unsubscribe.
        try:
            super(ServiceSubscribable, self
                  ).unsubscribe(reference, event_type, filter)
        except NotFoundError:
            next_service = queryNextService(self,
                                            self._serviceName)
            if next_service is not None:
                next_service.unsubscribe(reference, event_type, filter)
            else:
                raise

    def unsubscribeAll(self, reference, event_type=IEvent,
                       local_only=False):
        # unsubscribe all from here, and from the next service

        # n is the number of subscriptions removed
        n = super(ServiceSubscribable, self
                  ).unsubscribeAll(reference, event_type)
        if not local_only:
            next_service = queryNextService(self, self._serviceName)
            if next_service is not None:
                n += next_service.unsubscribeAll(reference, event_type)
        return n

    def resubscribeByHubId(self, reference):
        n = super(ServiceSubscribable, self
                  ).resubscribeByHubId(reference)
        next_service = queryNextService(self, self._serviceName)
        if next_service is not None:
            n += next_service.resubscribeByHubId(reference)
        return n

    def resubscribeByPath(self, reference):
        n = super(ServiceSubscribable, self
                  ).resubscribeByPath(reference)
        next_service = queryNextService(self, self._serviceName)
        if next_service is not None:
            n += next_service.resubscribeByPath(reference)
        return n

    def iterSubscriptions(self, reference=None, event_type=IEvent,
                          local_only=False):
        'See ISubscriptionService'
        subs = super(ServiceSubscribable, self
                     ).iterSubscriptions(reference, event_type)
        for subscription in subs:
            yield subscription

        if not local_only:
            next_service = queryNextService(self, self._serviceName)
            if next_service is not None:
                for subscription in next_service.iterSubscriptions(
                    reference, event_type):
                    yield subscription


from zope.app.site.interfaces import ISimpleService

class EventService(ServiceSubscriberEventChannel, ServiceSubscribable,
                   Contained):

    implements(IEventService, ISubscriptionService, ISimpleService)

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

    def notify(wrapped_self, event):
        "see ISubscriber"
        clean_self = removeAllProxies(wrapped_self)
        publishedEvents = getattr(clean_self, "_v_publishedEvents", [])
        if event not in publishedEvents:
            clean_self._notify(wrapped_self, event)

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

    def unbound(self, name):
        "See IBindingAware"
        # An event service is bound as EventSubscription and EventPublication.
        # We only want to unsubscribe from the next event service when
        # we're unbound as EventSubscription
        if name == EventSubscription:
            clean_self = removeAllProxies(self)

            # This flag is used by the unsubscribedFrom method (below) to
            # determine that it doesn't need to further unsubscribe beyond
            # what we're already doing.
            clean_self._v_unbinding = True
            try:
                super(EventService, self).unbound(name)
            finally:
                # unset flag
                del clean_self._v_unbinding

    def unsubscribedFrom(self, subscribable, event_type, filter):
        "See ISubscribingAware"
        super(EventService, self
              ).unsubscribedFrom(subscribable, event_type, filter)
        clean_self = removeAllProxies(self)
        if getattr(clean_self, "_v_unbinding", None) is None:
            # we presumably have been unsubscribed from a higher-level
            # event service because that event service is unbinding
            # itself: we need to remove the higher level event service
            # from our subscriptions list and try to find another event
            # service to which to attach
            clean_subscribable = removeAllProxies(subscribable)
            if ISubscriptionService.providedBy(
                removeAllProxies(clean_subscribable)):
                try:
                    context = zapi.getService(self, EventSubscription)
                    # we do this instead of getNextService because the order
                    # of unbinding and notification of unbinding is not
                    # guaranteed
                    while removeAllProxies(context) in (
                        clean_subscribable, clean_self): 
                        context = getNextService(context, EventSubscription)
                except ComponentLookupError:
                    pass
                else:
                    context.subscribe(self)

