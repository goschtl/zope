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
$Id: globalservice.py,v 1.15 2004/03/06 17:48:49 jim Exp $
"""

__metaclass__ = type

from zope.interface.type import TypeRegistry
from zope.interface import implements
from zope.exceptions import NotFoundError
from zope.proxy import removeAllProxies

from zope.app.event.interfaces import IEvent, ISubscriber, ISubscribingAware
from zope.app.event.interfaces import IGlobalSubscribable, IPublisher

import logging
import pprint
from StringIO import StringIO

def checkEventType(event_type, allow_none=False):
    if not (
        (allow_none and event_type is None)
        or event_type.extends(IEvent, strict=False)
        ):
        raise TypeError('event_type must extend IEvent: %s' % repr(event_type))

class Logger:
    """Class to log all events sent out by an event service.

    This is an event subscriber that you can add via ZCML to log all
    events sent out by Zope.
    """

    implements(ISubscriber)

    def __init__(self, severity=logging.INFO):
        self.severity = severity
        self.logger = logging.getLogger("Event.Logger")

    def notify(self, event):
        c = event.__class__
        detail = StringIO()
        data = event.__dict__.items()
        data.sort()
        # XXX The detail output could be improved.  Not sure what is wanted.
        pprint.pprint(data, detail)
        self.logger.log(self.severity, "%s.%s: %s",
                        c.__module__, c.__name__, detail.getvalue())


class GlobalSubscribable:
    """A global mix-in"""

    implements(IGlobalSubscribable)

    def __init__(self):
        self._registry = TypeRegistry()
        self._subscribers = [] # use dict?

    _clear = __init__

    def globalSubscribe(self, subscriber, event_type=IEvent, filter=None):
        checkEventType(event_type)
        clean_subscriber = removeAllProxies(subscriber)

        subscribingaware = ISubscribingAware(subscriber, None)
        if subscribingaware is not None:
            subscribingaware.subscribedTo(self, event_type, filter)

        if event_type is IEvent:
            event_type = None # optimization

        subscribers = self._registry.setdefault(event_type, [])
        subscribers.append((clean_subscriber, filter))

        for sub in self._subscribers:
            if sub[0] == clean_subscriber:
                try:
                    sub[1][event_type] += 1
                except KeyError:
                    sub[1][event_type] = 1
                break
        else:
            self._subscribers.append((clean_subscriber, {event_type: 1}))

        # Trigger persistence, if pertinent
        # self._registry = self._registry


    def unsubscribe(self, subscriber, event_type=None, filter=None):
        checkEventType(event_type, allow_none=True)
        clean_subscriber = removeAllProxies(subscriber)

        for subscriber_index in range(len(self._subscribers)):
            sub = self._subscribers[subscriber_index]
            if sub[0] == clean_subscriber:
                ev_set = sub[1]  # the dict of type:subscriptionCount
                break
        else:
            if event_type is not None:
                raise NotFoundError(subscriber)
            else:
                # this was a generic unsubscribe all request; work may have
                # been done by a local service
                return

        subscribingaware = ISubscribingAware(subscriber, None)

        if event_type:
            ev_type = event_type
            if event_type is IEvent:
                ev_type = None  # handle optimization
            if ev_type not in ev_set:
                raise NotFoundError(subscriber, event_type, filter)
            subscriptions = self._registry.get(ev_type)
            if not subscriptions:
                raise NotFoundError(subscriber, event_type, filter)
            try: 
                subscriptions.remove((clean_subscriber, filter))
            except ValueError:
                raise NotFoundError(subscriber, event_type, filter)
            if subscribingaware is not None:
                subscribingaware.unsubscribedFrom(self, event_type, filter)
            ev_set[ev_type] -= 1
            if ev_set[ev_type] < 1:
                for asubscriber, afilter in subscriptions:
                    if asubscriber == clean_subscriber:
                        break
                else:
                    if len(ev_set) > 1:
                        del ev_set[ev_type]
                    else:  # len(ev_set) == 1, and we just eliminated it
                        del self._subscribers[subscriber_index]
        else:
            for ev_type in ev_set:
                subscriptions = self._registry.get(ev_type)
                if ev_type is None:
                    ev_type = IEvent
                subs = subscriptions[:]
                subscriptions[:] = []
                for asubscriber, afilter in subs:
                    if asubscriber == clean_subscriber:
                        # deleted (not added back)
                        if subscribingaware is not None:
                            subscribingaware.unsubscribedFrom(
                                    self, ev_type, afilter)
                    else:
                        # kept (added back)
                        subscriptions.append(sub)
            del self._subscribers[subscriber_index]
        # Trigger persistence, if pertinent
        # self._registry = self._registry

    def listSubscriptions(self, subscriber, event_type=None):
        checkEventType(event_type, allow_none=True)
        subscriber = removeAllProxies(subscriber)

        result = []
        if event_type:
            ev_type = event_type
            if event_type is IEvent:
                ev_type = None # handle optimization
            subscriptions = self._registry.get(ev_type)
            if subscriptions:
                for sub in subscriptions:
                    if sub[0] == subscriber:
                        result.append((event_type, sub[1]))
        else:
            for subscriber_index in range(len(self._subscribers)):
                sub = self._subscribers[subscriber_index]
                if sub[0] == subscriber:
                    ev_set = sub[1]
                    break
            else:
                return result
            for ev_type in ev_set:
                subscriptions = self._registry.get(ev_type)
                if subscriptions:
                    if ev_type is None:
                        ev_type = IEvent
                    for sub in subscriptions:
                        if sub[0] == subscriber:
                            result.append((ev_type, sub[1]))
        return result


def globalNotifyOrPublish(self, event):
    assert IEvent.providedBy(event)
    subscriptionsForEvent = self._registry.getAllForObject(event)
    for subscriptions in subscriptionsForEvent:
        for subscriber, filter in subscriptions:
            if filter is not None and not filter(event):
                continue
            ISubscriber(subscriber).notify(event)

class GlobalEventChannel(GlobalSubscribable):

    implements(IGlobalSubscribable, ISubscriber)

    notify = globalNotifyOrPublish


class GlobalEventPublisher(GlobalSubscribable):

    implements(IGlobalSubscribable, IPublisher)

    publish = globalNotifyOrPublish


# Repeated here, and in zope/app/event/__init__.py to avoid circular import.
def globalSubscribeMany(subscriber, event_types=(IEvent,), filter=None):
    subscribe_func = eventPublisher.globalSubscribe
    for event_type in event_types:
        subscribe_func(subscriber, event_type, filter)

eventPublisher = GlobalEventPublisher()
eventLogger = Logger()

_clear = eventPublisher._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp

