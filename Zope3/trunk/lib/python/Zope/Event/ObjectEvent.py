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
$Id: ObjectEvent.py,v 1.2 2002/06/10 23:29:25 jim Exp $
"""

from IObjectEvent import IObjectAddedEvent, IObjectModifiedEvent
from IObjectEvent import IObjectRemovedEvent, IObjectMovedEvent

class ObjectAddedEvent:
    """An object has been added to a container."""

    __implements__ = IObjectAddedEvent

    def __init__(self, location):
        self.__location = location
        
    def getLocation(self):        
        """returns the object location after it has been added to the container"""
        return self.__location

class ObjectModifiedEvent(ObjectAddedEvent):
    """An object has been modified"""

    __implements__ = IObjectModifiedEvent

class ObjectRemovedEvent:
    """An object has been removed from a container"""

    __implements__ = IObjectRemovedEvent


    def __init__(self, location, obj):
        self.__location = location
        self.__obj = obj
        
    def getLocation(self):        
        """returns the location the object was removed from"""
        return self.__location
        
    def getObject(self):
        """returns the object that was removed."""
        return self.__obj


class ObjectMovedEvent(ObjectAddedEvent):
    """An object has been moved"""

    __implements__ = IObjectMovedEvent

    def __init__(self, from_location, location):
        ObjectAddedEvent.__init__(self, location)
        self.__from_location = from_location
        
    def getFromLocation(self):
        """location of the object before it was moved"""
        return self.__from_location
