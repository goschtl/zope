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
$Id: __init__.py,v 1.14 2004/04/27 10:53:45 jim Exp $
"""
from zope.component import getService
from zope.app.servicenames import EventPublication
from zope.app.event.interfaces import IEvent
from zope.app.event.globalservice import eventPublisher

def getEventService(context): # the "publish" service
    return getService(context, EventPublication)

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

