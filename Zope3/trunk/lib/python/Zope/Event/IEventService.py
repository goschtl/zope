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
$Id: IEventService.py,v 1.6 2002/12/05 17:20:29 stevea Exp $
"""

from ISubscribable import ISubscribable
from IEvent import IEvent

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

class IGlobalEventService(IEventService):
    """The global event-service does not allow normal subscriptions.

    Subscriptions to the global event-service are not persistent.
    If you want to subscribe to the global event-service, you need
    to use the 'globalSubscribe' method instead of the 'subscribe'
    method.
    """

    def subscribe(subscriber, event_type=IEvent, filter=None):
        """Raises NotImplementedError."""

    def globalSubscribe(subscriber, event_type=IEvent, filter=None):
        """Add subscriber to the list of subscribers for the channel."""

