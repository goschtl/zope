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
$Id: metaconfigure.py,v 1.2 2002/12/25 14:12:51 jim Exp $
"""

from zope.configuration.action import Action

from zope.app.event import globalSubscribeMany
from zope.interfaces.event import IEvent
from zope.interface import Interface

counter = 0

def subscribe(_context, subscriber, event_types=(IEvent), filter=None):
    global counter
    counter += 1

    subscriber = _context.resolve(subscriber)

    event_type_names = event_types
    event_types=[]
    for event_type_name in event_type_names.split():
        event_types.append(_context.resolve(event_type_name))

    if filter is not None:
        filter = _context.resolve(filter)

    return [
        Action(
             # subscriptions can never conflict
             discriminator = ('subscribe', counter),
             callable = globalSubscribeMany,
             args = (subscriber, event_types, filter)
             ),
        Action(
            discriminator = None,
            callable = globalSubscribeMany,
            args = ('Interfaces', 'provideInterface',
                    type.__module__+'.'+type.__name__, type)
              )
        ]
