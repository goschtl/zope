##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: __init__.py,v 1.4 2003/01/27 18:16:20 stevea Exp $
"""

from zope.component import getService
from zope.app.interfaces.event import IEvent
from zope.app.event.globalservice import eventPublisher, checkEventType

def getEventService(context): # the "publish" service
    return getService(context, 'Events')

def publish(context, event):
    return getEventService(context).publish(event)

def globalSubscribe(subscriber, event_type=IEvent, filter=None):
    return eventPublisher.globalSubscribe(subscriber, event_type, filter)

def globalSubscribeMany(subscriber, event_types=(IEvent,), filter=None):
    subscribe_func = eventPublisher.globalSubscribe
    for event_type in event_types:
        subscribe_func(subscriber, event_type, filter)

def globalUnsubscribe(subscriber, event_type=None, filter=None):
    return eventPublisher.unsubscribe(subscriber, event_type, filter)

def globalListSubscriptions(subscriber, event_type=None):
    return eventPublisher.listSubscriptions(subscriber, event_type)

