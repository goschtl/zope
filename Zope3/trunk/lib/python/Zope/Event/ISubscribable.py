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
$Id: ISubscribable.py,v 1.3 2002/09/03 20:13:38 jim Exp $
"""

from Interface import Interface
from IEvent import IEvent

class ISubscribable(Interface):
    """Objects that broadcast events to subscribers."""

    def subscribe(subscriber, event_type=IEvent, filter=None):
        """Add subscriber to the list of subscribers for the channel.
        
        subscriber must implement ISubscriber.
        Probable subscriber types include the following:
        
            o Hard Reference (for placeless, global objects and event service)

                Simply register the subscriber directly, in which
                case, the subscription, and possibly the subscriber,
                is as persistent as the subscribable.  The subscriber
                will not be wrapped for context or security when
                called.

            o Soft reference (for placeful, local objects and event service)

                Register an object with a notify method and a path that
                dereferences the path and delegates notifications.

            o Location-independent reference (for placeful)

                Register an object with a notify method and an
                ObjectHub ruid that dereferences the ruid via the hub
                and delegates notifications.

            o Abstract reference (for both)

                Register an object with a notify method and an IReference that
                dereferences the IReference and delegates notifications.
        
        event_type, if supplied, is the event interface
        about which subscriber should be notified, and must implement
        IEvent.  The subscriber will be notified of all events of this
        event_type and of subclasses of this event_type.
        The default value, IEvent, as the parent type,
        is effectively a single catch-all event type that will pass all
        event types to the subscriber.

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
        
        The subscriber is matched via equality (not identity).
        
        If event_type is None, the default value, the subscriber is
        unsubscribed completely for all event types from this
        subscribable (and its parents, if the subscribable is a placeful
        service).  If no subscriptions for this subscriber are
        present, no error is raised.
        
        if event_type is supplied, this method will unsubscribe the
        subscriber from one subscription exactly matching the
        event_type/filter pair given (the default filter being None).
        If other subscriptions are present they will remain.  If the
        subscription cannot be found and the subscribable is a placeful
        service, the unsubscription request is passed to parent
        services.  Raises Zope.Exceptions.NotFound if subscriber wasn't 
        subscribed as expected.
        
        If the subscriber implements ISubscriptionAware, this function
        will call the subscriber's unsubscribedFrom method for each
        individual unsubscribe.
        """
        
    def listSubscriptions(subscriber, event_type=None):
        """returns an iterator of the subscriptions to this channel for
        the subscriber. if event_type is supplied, the list is limited
        to that exact event_type.  If the subscribable is a placeful
        service, the list will include subscriptions to parent services.
        The subscriber is matched via equality (not identity).  No
        subscriptions returns an empty iterator.  Each subscription is
        represented as a tuple (event_type, filter)."""
