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
$Id: __init__.py,v 1.2 2002/12/21 15:32:45 poster Exp $
"""

from Zope.Event.IEvent import IEvent
from Zope.Event import getEventService

def globalSubscribe(subscriber, event_type=IEvent, filter=None, context=None):
    if context is None:
        context = subscriber
    return getEventService(None).globalSubscribe(
        subscriber, event_type, filter)

def globalSubscribeMany(subscriber, event_types=(IEvent,),
                        filter=None, context=None):
    if context is None: context=subscriber
    subscribe_func = getEventService(None).globalSubscribe
    for event_type in event_types:
        subscribe_func(subscriber, event_type, filter)
