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
$Id: event.py,v 1.5 2003/02/03 15:59:12 stevea Exp $
"""

from zope.interface import Interface
from zope.app.interfaces.event import ISubscribable, ISubscriber, IPublisher
from zope.app.interfaces.event import IEvent

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

