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
$Id: __init__.py,v 1.4 2002/12/01 10:32:29 jim Exp $
"""

from Zope.ComponentArchitecture import getService
from IEvent import IEvent


def getEventService(context):
    return getService(context, 'Events')

def publish(context, event):
    return getEventService(context).publish(event)

def subscribe(subscriber, event_type=IEvent, filter=None, context=None):
    if context is None: context=subscriber
    return getEventService(context).subscribe(
        subscriber, event_type, filter)

def subscribeMany(subscriber, event_types=(IEvent,), filter=None, context=None):
    if context is None: context=subscriber
    es= getEventService(context).subscribe
    for event_type in event_types:
        es(subscriber, event_type, filter)

def unsubscribe(subscriber, event_type=None, filter=None, context=None):
    if context is None: context=subscriber
    return getEventService(context).unsubscribe(
        subscriber, event_type, filter)

def listSubscriptions(subscriber, event_type=None, context=None):
    if context is None: context=subscriber
    return getEventService(context).listSubscriptions(
        subscriber, event_type)



def _clear():
    from EventService import _clear; _clear()
