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
"""

Revision information:
$Id: event.py,v 1.4 2003/01/27 18:16:16 stevea Exp $
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

    def subscribe(subscriber, event_type=IEvent, filter=None):
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
        will be notified of events only if they pass.

        A subscriber may subscribe more than once, even if it has
        already been subscribed with the same event type and
        filter.  In this case the subscriber will receive multiple
        calls to its notify method.

        If the subscriber has an ISubscribingAware adapter, this method
        will call the subscriber's subscribedTo method.
        """

    def unsubscribe(subscriber, event_type=IEvent, filter=None):
        """Unsubscribe subscriber from receiving event types from this
        subscribable.

        Subscriber must implement ISubscriber, and must be accessible
        via path.  The reference passed to the method may be a hard 
        reference, contextually wrapped if appropriate; or a path or
        hubid that reference the subscriber.

        If the subscriber is a hard reference then it will be
        unsubscribed on the basis of both hubid, if available for the
        object, and path; passing the path or the hubid unsubscribes
        that only.

        unsubscribe must also accept paths and hubids that no longer
        resolve to an object, but if no subscriptions are found on the
        basis of the unicode string or integer, a NotFoundError is
        still raised.

        If event_type is None, the default value, the subscriber is
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
        the subscriber.

        Subscriber must must be accessible via path.
        The reference passed to the method may be a hard reference,
        contextually wrapped if appropriate; or a path or hubid that
        reference the subscriber.

        If the subscriber is a hard reference then it will return an
        iterator of subscriptions on the basis of both hubid, if
        available for the object, and path; passing the path or the
        hubid lists subscriptions for that only.

        If event_type is supplied, the list is limited
        to that exact event_type.  If the subscribable is a placeful
        service, the list will include subscriptions to parent services.
        No subscriptions returns an empty iterator.  Each subscription is
        represented as a tuple (event_type, filter)."""


class IObjectEvent(IEvent):
    """Something has happened to an object.

    The object that generated this event is not necessarily the object
    refered to by location.
    """

    object = Attribute("The subject of the event.")

    location = Attribute("An optional object location.")

class IObjectCreatedEvent(IObjectEvent):
    """An object has been created.

    The location will usually be None for this event."""

class IObjectAddedEvent(IObjectEvent):
    """An object has been added to a container."""

class IObjectModifiedEvent(IObjectEvent):
    """An object has been modified"""

class IObjectAnnotationsModifiedEvent(IObjectModifiedEvent):
    """An object's annotations have been modified"""

class IObjectContentModifiedEvent(IObjectModifiedEvent):
    """An object's content has been modified"""

class IObjectRemovedEvent(IObjectEvent):
    """An object has been removed from a container"""

class IObjectMovedEvent(IObjectEvent):
    """An object has been moved"""

    fromLocation = Attribute("The old location for the object.")

