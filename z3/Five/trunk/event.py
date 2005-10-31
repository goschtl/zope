##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Five event definitions.

$Id$
"""

import warnings

from zope.interface import implements
from zope.interface import Attribute
from zope.app.event.interfaces import IObjectEvent
from zope.app.event.objectevent import ObjectEvent


class IObjectWillBeMovedEvent(IObjectEvent):
    """An object will be moved."""
    oldParent = Attribute("The old location parent for the object.")
    oldName = Attribute("The old location name for the object.")
    newParent = Attribute("The new location parent for the object.")
    newName = Attribute("The new location name for the object.")

class IObjectWillBeAddedEvent(IObjectWillBeMovedEvent):
    """An object will be added to a container."""

class IObjectWillBeRemovedEvent(IObjectWillBeMovedEvent):
    """An object will be removed from a container"""

class IFiveObjectClonedEvent(IObjectEvent):
    """An object has been cloned (a la Zope 2).

    This is for Zope 2 compatibility, subscribers should really use
    IObjectCopiedEvent or IObjectAddedEvent, depending on their use
    cases.

    event.object is the copied object, already added to its container.
    Note that this event is dispatched to all sublocations.
    """


class ObjectWillBeMovedEvent(ObjectEvent):
    """An object will be moved"""
    implements(IObjectWillBeMovedEvent)

    def __init__(self, object, oldParent, oldName, newParent, newName):
        ObjectEvent.__init__(self, object)
        self.oldParent = oldParent
        self.oldName = oldName
        self.newParent = newParent
        self.newName = newName

class ObjectWillBeAddedEvent(ObjectWillBeMovedEvent):
    """An object will be added to a container"""
    implements(IObjectWillBeAddedEvent)

    def __init__(self, object, newParent=None, newName=None):
        #if newParent is None:
        #    newParent = object.__parent__
        #if newName is None:
        #    newName = object.__name__
        ObjectWillBeMovedEvent.__init__(self, object, None, None,
                                        newParent, newName)

class ObjectWillBeRemovedEvent(ObjectWillBeMovedEvent):
    """An object will be removed from a container"""
    implements(IObjectWillBeRemovedEvent)

    def __init__(self, object, oldParent=None, oldName=None):
        #if oldParent is None:
        #    oldParent = object.__parent__
        #if oldName is None:
        #    oldName = object.__name__
        ObjectWillBeMovedEvent.__init__(self, object, oldParent, oldName,
                                        None, None)

class FiveObjectClonedEvent(ObjectEvent):
    implements(IFiveObjectClonedEvent)

