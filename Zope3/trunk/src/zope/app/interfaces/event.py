##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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
$Id: event.py,v 1.2 2002/12/25 14:12:56 jim Exp $
"""

from zope.interfaces.event import IEvent
from zope.interfaces.event import IEventService

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

"""

Revision information:
$Id: event.py,v 1.2 2002/12/25 14:12:56 jim Exp $
"""

from zope.interfaces.event import IEvent
from zope.interface import Attribute

class IObjectEvent(IEvent):
    """Something has happened to an object.

    The object that generated this event is not necessarily the object
    refered to by location.
    """

    object = Attribute("The subject of the event.")

    location = Attribute("An optional object location.")

class IObjectCreatedEvent(IObjectEvent):
    """An object has been created.

    The location will usually be None for this event."""

class IObjectAddedEvent(IObjectEvent):
    """An object has been added to a container."""

class IObjectModifiedEvent(IObjectEvent):
    """An object has been modified"""

class IObjectAnnotationsModifiedEvent(IObjectModifiedEvent):
    """An object's annotations have been modified"""

class IObjectContentModifiedEvent(IObjectModifiedEvent):
    """An object's content has been modified"""


class IObjectRemovedEvent(IObjectEvent):
    """An object has been removed from a container"""

class IObjectMovedEvent(IObjectEvent):
    """An object has been moved"""

    fromLocation = Attribute("The old location for the object.")
