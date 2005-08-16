##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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
"""Event-related interfaces

$Id: interfaces.py,v 1.3 2004/03/11 08:14:02 srichter Exp $
"""
from zope.interface import Interface, Attribute

class IEvent(Interface):
    """The base interface for Events."""


class IFilter(Interface):
    """Interface for predicates used to filter events."""

    def __call__(event):
        """Return True if event passes, otherwise False."""


class IPublisher(Interface):

    def publish(event):
        """Publish this event to subscribers.

        Events will often be propagated to higher level IPublishers.
        This is a policy decision for the IPublisher.
        """


# these are method calls and not events because they are traditional messages
# between two objects, not events of general interest.
class ISubscribingAware(Interface):

    def subscribedTo(subscribable, event_type, filter):
        """Alerts the object that it has subscribed, via a call from
        itself or from another object, to the subscribable.  The
        event_type and filter match the arguments provided to the
        ISubscribable.subscribe.

        The subscribable must be appropriately placefully wrapped (note
        that the global event service will have no wrapping)."""

    def unsubscribedFrom(subscribable, event_type, filter):
        """Alerts the object that it has unsubscribed, via a call from
        itself or from another object, to the subscribable.  The
        event_type and filter match the exact event_type and filter of
        the deleted subscription, rather than, necessarily, the
        arguments provided to the ISubscribable.unsubscribe.

        The subscribable must be appropriately placefully wrapped (note
        that the global event service will have no wrapping)."""


class ISubscriber(Interface):
    """Interface for objects which receiving event notifications."""

    def notify(event):
        """ISubscribables call this method to indicate an event.

        This method must not block.

        This method may raise an exception to veto the event.
        """


class IGlobalSubscribable(Interface):
    """Objects that broadcast events to subscribers.

    Subscriptions to a global subscribable are not persistent."""

    def globalSubscribe(subscriber, event_type=IEvent, filter=None):
        """Add subscriber to the list of subscribers for the channel.

        subscriber must be adaptable to ISubscriber.

        event_type, if supplied, is the event interface
        about which subscriber should be notified, and must implement
        IEvent.  The subscriber will be notified of all events of this
        event_type and of subclasses of this event_type.
        The default value, IEvent, as the parent type, is effectively a single
        catch-all event type that will pass all event types to the subscriber.

        filter, if supplied, must implement IFilter; subscriber
        will be notified of events only if they pass.

        A subscriber may subscribe more than once, even if it has
        already been subscribed with the same event type and
        filter.  In this case the subscriber will receive multiple
        calls to its notify method.

        If the subscriber has an ISubscribingAware adapter, this function
        will call the subscriber's subscribedTo method.
        """

    def unsubscribe(subscriber, event_type=IEvent, filter=None):
        """Unsubscribe subscriber from receiving event types from this
        subscribable.

        If event_type is IEvent, the default value, the subscriber is
        unsubscribed completely for all event types from this
        subscribable (and its parents, if the subscribable is a placeful
        service).  The filter argument is ignored in this case.  If no
        subscriptions for this subscriber are present, no error is
        raised.

        If event_type is supplied, this method will unsubscribe the
        subscriber from one subscription exactly matching the
        event_type/filter pair given (the default filter being None).
        If other subscriptions are present they will remain.  If the
        subscription cannot be found and the subscribable is a placeful
        service, the unsubscription request is passed to parent
        services.  Raises Zope.Exceptions.NotFound if subscriber wasn't 
        subscribed as expected.

        If the subscriber has an ISubscribingAware adapter, this function
        will call the subscriber's unsubscribedFrom method for each
        individual unsubscribe.
        """

    def listSubscriptions(subscriber, event_type=IEvent):
        """Returns an iterator of the subscriptions to this channel for
        the subscriber. If event_type is supplied, the list is limited
        to that exact event_type.  If the subscribable is a placeful
        service, the list will include subscriptions to parent services.
        No subscriptions returns an empty iterator.  Each subscription is
        represented as a tuple (event_type, filter)."""


class ISubscribable(Interface):
    """A subscribable that only works with physically locatable objects,
    or their paths or hubids."""

    def subscribe(reference, event_type=IEvent, filter=None):
        """Add subscriber to the list of subscribers for the component.

        Subscriber must have an ISubscriber adapter, and must be accessible
        via path.  The reference passed to the method may be a hard 
        reference, contextually wrapped if appropriate; or a path or
        hubid that reference the subscriber.

        If the subscriber is a wrapped object then it will be
        subscribed on the basis of hubid, if available for the object,
        and path otherwise; passing the path or the hubid uses that
        explicitly.  In all cases, the method passes back the hubid or
        path used to subscribe on success.

        event_type, if supplied, is the event interface
        about which subscriber should be notified, and must implement
        IEvent.  The subscriber will be notified of all events of this
        event_type and of subclasses of this event_type.
        The default value, IEvent, as the parent type, is effectively a
        single catch-all event type that will pass all event types to
        the subscriber.

        filter, if supplied, must implement IFilter; subscriber
        will be notified of events only if they pass. filter must be
        picklable.

        A subscriber may subscribe more than once, even if it has
        already been subscribed with the same event type and
        filter.  In this case the subscriber will receive multiple
        calls to its notify method.

        If the subscriber has an ISubscribingAware adapter, this method
        will call the subscriber's subscribedTo method.
        """

    def unsubscribe(reference, event_type, filter=None):
        """Removes just one subscription.

        This is in parity with subscribe providing just one subscription.

        A filter of None means 'the subscription with no filter' rather
        than 'a subscription with any filter'.

        A subscriber is determined based on the reference supplied.

        If 'reference' is an object, it must be physically locatable so
        we can get its path. We try to remove a subscription based on the
        hubId (if available). If there is no hubId or no such subscription,
        we try to remove a subscription based on the path.

        If 'reference' is an int, it is interpreted as a hubId. We try to
        remove a subscription by hubId, and then by path.

        If 'reference' is a string or unicode, it is interpreted as an
        absolute path. We try to remove a subscription by path, and then
        by hubId.

        If a subscription is removed, and the subscriber has an
        ISubscribingAware adapter, the adapter's unsubscribedFrom method
        is called.
        If no subscription can be removed, we raise a NotFoundError.

        If a path or hubId is given that no longer resolves to an object,
        and such a subscription exists, then that subscription will be
        removed and a warning logged.
        """

    def unsubscribeAll(reference, event_type=IEvent):
        """Removes all subscriptions for subscriber that match event_type.

        The subscriber is determined from the reference as described in
        the docstring of the 'unsubscribe' method.

        If a path and hubId can be determined for the subscriber,
        all subscriptions by both path and hubId that match event_type
        are removed.

        Subscriptions are removed only if the event in the subscription
        is event_type, or extends event_type.

        Returns the number of subscriptions removed.
        """

    def resubscribeByHubId(reference):
        """Change all subscriptions for reference by path into subscriptions
        by hubId.

        The reference may be a hubId, a path or a physically locatable object.

        Returns the number of subscriptions converted.
        """

    def resubscribeByPath(reference):
        """Change all subscriptions for reference by hubId into subscriptions
        by path.

        The reference may be a hubId, a path or a physically locatable object.

        Returns the number of subscriptions converted.
        """

    def iterSubscriptions(reference=None, event_type=IEvent):
        """Returns an iterator of the subscriptions to this channel for
        the referenced subscriber.

        The reference may be a hubId, a path or a physically locatable object.
        Subscriptions by hubId and by path are returned.
        The reference may also be None, meaning that subscriptions for all
        subscribers are to be returned.

        If event_type is supplied, only those subscriptions where the
        event_type of the subscription extends or is equal to the given
        event_type will be returned.

        Each element of the iteration is a three-tuple:

          (reference, event_type, filter)

        The first element of the tuple will the int or unicode that is
        subscribed. The second element is the event_type subscribed.
        The third is the filter subscribed.
        """

class ISubscriptionService(ISubscribable):
    """A Subscribable that implements the Subscription service."""
    def unsubscribe(reference, event_type, filter=None):
        '''See ISubscribable.unsubscribe

        In addition, if the reference cannot be unsubscribed in this service,
        pass this on to the next service.
        '''

    def unsubscribeAll(reference, event_type=IEvent, local_only=False):
        '''See ISubscribable.unsubscribeAll

        If local_only is True, only subscriptions to this event service
        instance are removed.
        Otherwise, the unsubscribeAll request is passed on to the next
        service.
        '''

    def resubscribeByHubId(reference):
        '''See ISubscribable.resubscribeByHubId

        In addition, the request is passed on to the next service.
        '''

    def resubscribeByPath(reference):
        '''See ISubscribable.resubscribeByPath

        In addition, the request is passed on to the next service.
        '''

    def iterSubscriptions(reference, event_type=IEvent, local_only=False):
        '''See ISubscribable.iterSubscriptions

        If local_only is True, only subscriptions to this event service
        instance are returned.
        Otherwise, after subscriptions to this event service, subscriptions
        to the next event service are returned.
        '''

class IEventChannel(ISubscribable, ISubscriber):
    """Interface for objects which distribute events to subscribers. """

class IEventService(ISubscriptionService, IPublisher):
    """Local event service implementation.

    Offers the Events and Subscription services.
    """


class IObjectEvent(IEvent):
    """Something has happened to an object.

    The object that generated this event is not necessarily the object
    refered to by location.
    """

    object = Attribute("The subject of the event.")

class IObjectCreatedEvent(IObjectEvent):
    """An object has been created.

    The location will usually be None for this event."""

class IObjectCopiedEvent(IObjectCreatedEvent):
    """An object has been copied"""

class IObjectModifiedEvent(IObjectEvent):
    """An object has been modified"""

class IObjectAnnotationsModifiedEvent(IObjectModifiedEvent):
    """An object's annotations have been modified"""

class IObjectContentModifiedEvent(IObjectModifiedEvent):
    """An object's content has been modified"""

class IDatabaseOpenedEvent(IEvent):
    """The main database has been opened."""

    database = Attribute("The main database.")

class IProcessStartingEvent(IEvent):
    """The application server process is starting."""
