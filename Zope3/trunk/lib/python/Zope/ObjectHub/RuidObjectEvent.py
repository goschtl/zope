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
$Id: RuidObjectEvent.py,v 1.2 2002/06/10 23:29:29 jim Exp $
"""

from IRuidObjectEvent import IRuidObjectRegisteredEvent
from IRuidObjectEvent import IRuidObjectAddedEvent
from IRuidObjectEvent import IRuidObjectUnregisteredEvent
from IRuidObjectEvent import IRuidObjectModifiedEvent
from IRuidObjectEvent import IRuidObjectContextChangedEvent
from IRuidObjectEvent import IRuidObjectRemovedEvent

class RuidObjectEvent:
    """Convenient mix-in for RuidObjectEvents"""
    
    def __init__(self, objecthub, ruid, location):
        # we keep all three, to avoid unnecessary lookups
        # and to give the objecthub an opportunity to do
        # caching of objects
        self.__objecthub = objecthub
        self.__ruid = ruid
        self.__location = location
        
    def getRuid(self):
        return self.__ruid
        
    def getLocation(self):
        return self.__location
        
    def getObject(self):
        if hasattr(self, '_v_object'):
            return self._v_object
        obj = self._v_object = self.__objecthub.getObject(self.__ruid)
        return obj


class RuidObjectRegisteredEvent(RuidObjectEvent):
    """An ruid has been freshly created and mapped against an object."""

    __implements__ = IRuidObjectRegisteredEvent


class RuidObjectUnregisteredEvent(RuidObjectEvent):
    """We are no longer interested in this object."""

    __implements__ = IRuidObjectUnregisteredEvent


class RuidObjectAddedEvent(RuidObjectEvent):
    """An ruid has been freshly created and mapped against an object.
       Also, implies the object has been newly added."""
    
    __implements__ = IRuidObjectAddedEvent
    
    
class RuidObjectModifiedEvent(RuidObjectEvent):
    """An object with an ruid has been modified."""
    
    __implements__ = IRuidObjectModifiedEvent
    
    
class RuidObjectContextChangedEvent(RuidObjectEvent):
    """An object with an ruid has had its context changed. Typically, this
       means that it has been moved."""
       
    __implements__ = IRuidObjectContextChangedEvent


class RuidObjectRemovedEvent(RuidObjectEvent):
    """An object with an ruid has been removed."""

    __implements__ = IRuidObjectRemovedEvent

    def __init__(self, obj, ruid, location):
        self.__object = obj
        self.__ruid = ruid
        self.__location = location

    def getRuid(self):
        return self.__ruid
        
    def getLocation(self):
        return self.__location

    def getObject(self):
        return self.__object
