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
"""Object lifetime events.

$Id: objectevent.py,v 1.3 2003/02/11 15:59:44 sidnei Exp $
"""

__metaclass__ = type

from zope.app.interfaces.event import IObjectEvent, IObjectCreatedEvent
from zope.app.interfaces.event import IObjectAddedEvent, IObjectModifiedEvent
from zope.app.interfaces.event import IObjectRemovedEvent, IObjectMovedEvent
from zope.app.interfaces.event import IObjectCopiedEvent
from zope.app.interfaces.event import IObjectAnnotationsModifiedEvent
from zope.app.interfaces.event import IObjectContentModifiedEvent
from zope.app.traversing import getPhysicalPath

_marker = object()

class ObjectEvent:
    """Something has happened to an object"""

    __implements__ = IObjectEvent

    def _getLocation(self):
        if self.__location is not _marker:
            return self.__location
        return getPhysicalPath(self.object)

    location = property(_getLocation)

    def __init__(self, object, location=_marker):
        self.object = object
        self.__location = location

class ObjectAddedEvent(ObjectEvent):
    """An object has been added to a container"""

    __implements__ = IObjectAddedEvent

class ObjectCreatedEvent(ObjectEvent):
    """An object has been created"""

    __implements__ = IObjectCreatedEvent

class ObjectModifiedEvent(ObjectEvent):
    """An object has been modified"""

    __implements__ = IObjectModifiedEvent

class ObjectAnnotationsModifiedEvent(ObjectModifiedEvent):
    """An object's annotations have been modified"""

    __implements__ = IObjectAnnotationsModifiedEvent

class ObjectContentModifiedEvent(ObjectModifiedEvent):
    """An object's content has been modified"""

    __implements__ = IObjectContentModifiedEvent

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

class ObjectCopiedEvent(ObjectAddedEvent):
    """An object has been copied"""

    __implements__ = IObjectCopiedEvent

    fromLocation = None

    def __init__(self, object, from_location, to_location):
        super(ObjectCopiedEvent, self).__init__(object, to_location)
        self.fromLocation = from_location
