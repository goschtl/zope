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
$Id: ObjectEvent.py,v 1.3 2002/10/03 20:53:22 jim Exp $
"""

__metaclass__ = type

from IObjectEvent import IObjectEvent, IObjectCreatedEvent
from IObjectEvent import IObjectAddedEvent, IObjectModifiedEvent
from IObjectEvent import IObjectRemovedEvent, IObjectMovedEvent

class ObjectEvent:
    """An object has been added to a container."""

    __implements__ = IObjectEvent

    object = None
    location = None

    def __init__(self, object, location=None):
        self.object = object
        self.location = location

class ObjectAddedEvent(ObjectEvent):
    """An object has been added"""

    __implements__ = IObjectAddedEvent

class ObjectModifiedEvent(ObjectEvent):
    """An object has been modified"""

    __implements__ = IObjectModifiedEvent

class ObjectRemovedEvent(ObjectEvent):
    """An object has been removed from a container"""

    __implements__ = IObjectRemovedEvent


class ObjectMovedEvent(ObjectAddedEvent):
    """An object has been moved"""

    __implements__ = IObjectMovedEvent

    fromLocation = None

    def __init__(self, object, from_location, to_location):
        super(ObjectMovedEvent, self).__init__(object, to_location)
        self.fromLocation = from_location
