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
$Id: event.py,v 1.2 2002/12/25 14:15:12 jim Exp $
"""

from zope.interface import Interface

class IEvent(Interface):
    """The Base interface for Events"""


"""

Revision information:
$Id: event.py,v 1.2 2002/12/25 14:15:12 jim Exp $
"""

from zope.interface import Interface

class IEventFilter(Interface):
    """Interface for predicates used to filter events."""

    def __call__(event):
        """Return true if event passes, or false."""


"""

Revision information:
$Id: event.py,v 1.2 2002/12/25 14:15:12 jim Exp $
"""

from zope.interface import Interface


class ISubscribable(Interface):
    """Objects that broadcast events to subscribers."""

    def subscribe(subscriber, event_type=IEvent, filter=None):
        """Add subscriber to the list of subscribers for the channel.

        subscriber must implement ISubscriber.

        event_type, if supplied, is the event interface
        about which subscriber should be notified, and must implement
        IEvent.  The subscriber will be notified of all events of this
        event_type and of subclasses of this event_type.
        The default value, IEvent, as the parent type, is effectively a single
        catch-all event type that will pass all event types to the subscriber.

        filter, if supplied, must implement IEventFilter; subscriber
        will be notified of events only if they pass.

        A subscriber may subscribe more than once, even if it has
        already been subscribed with the same event type and
        filter.  In this case the subscriber will receive multiple
        calls to its notify method.

        If the subscriber implements ISubscriptionAware, this function
        will call the subscriber's subscribedTo method.
        """

    def unsubscribe(subscriber, event_type=None, filter=None):
        """Unsubscribe subscriber from receiving event types from this
        subscribable.

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
        services.  Raises NotFound if subscriber wasn't
        subscribed as expected.

        If the subscriber implements ISubscriptionAware, this function
        will call the subscriber's unsubscribedFrom method for each
        individual unsubscribe.
        """

    def listSubscriptions(subscriber, event_type=None):
        """Returns an iterator of the subscriptions to this channel for
        the subscriber. If event_type is supplied, the list is limited
        to that exact event_type.  If the subscribable is a placeful
        service, the list will include subscriptions to parent services.
        The subscriber is matched via equality (not identity).  No
        subscriptions returns an empty iterator.  Each subscription is
        represented as a tuple (event_type, filter)."""


"""

Revision information:
$Id: event.py,v 1.2 2002/12/25 14:15:12 jim Exp $
"""

from zope.interface import Interface

class ISubscriber(Interface):
    """Interface for objects which receiving event notifications."""

    def notify(event):
        """ISubscribables call this method to indicate an event.

        This method must not block!

        This method may raise an exception to veto the event.
        """

class IIndirectSubscriber(ISubscriber):
    """Interface for objects that handle subscriptions for another object."""

    def __eq__(other):
        """Compare two indirect subscribers

        Two indirect subscribers are the same if they reference the
        same object.
        """





"""

Revision information:
$Id: event.py,v 1.2 2002/12/25 14:15:12 jim Exp $
"""




class IEventChannel(ISubscribable, ISubscriber):
    """Interface for objects which distribute events to subscribers. """




"""

Revision information:
$Id: event.py,v 1.2 2002/12/25 14:15:12 jim Exp $
"""
from zope.interface import Interface

# these are method calls and not events because they are traditional messages
# between two objects, not events of general interest.

class ISubscriptionAware(Interface):

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


"""

Revision information:
$Id: event.py,v 1.2 2002/12/25 14:15:12 jim Exp $
"""




class IEventService(ISubscribable):
    """The EventService service is the 'root channel'.

    Its subscribers include other channels.

    It is also the 'default destination' for events
    when they are generated.
    """

    def publish(event):
        """Notify all subscribers of the channel of event.

        Events will often be propagated to higher level IEventServices;
        This is a policy decision for the IEventService.
        """
