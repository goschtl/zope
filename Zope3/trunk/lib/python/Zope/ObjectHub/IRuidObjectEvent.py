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
$Id: IRuidObjectEvent.py,v 1.2 2002/06/10 23:29:29 jim Exp $
"""
from Zope.Event.IEvent import IEvent

class IRuidObjectEvent(IEvent):
    """Something has happened to an object for which there is an ruid.
       An ruid is a way or refering to an object independent of location.
    """

    def getRuid():
        """Returns the object's ruid."""
        
    def getLocation():
        """Returns the object's current location."""
        
    def getObject():
        """Returns the object."""
        


class IRuidObjectRegisteredEvent(IRuidObjectEvent):
    """An ruid has been freshly created and mapped against an object."""


class IRuidObjectUnregisteredEvent(IRuidObjectEvent):
    """We are no longer interested in this object."""


class IRuidObjectAddedEvent(IRuidObjectRegisteredEvent):
    """An ruid has been freshly created and mapped against an object.
       Also, implies the object has been newly added."""
    
    
class IRuidObjectModifiedEvent(IRuidObjectEvent):
    """An object with an ruid has been modified."""
    
    
class IRuidObjectContextChangedEvent(IRuidObjectEvent):
    """An object with an ruid has had its context changed. Typically, this
       means that it has been moved."""

       
class IRuidObjectRemovedEvent(IRuidObjectUnregisteredEvent):
    """An object with an ruid has been removed."""

    def getLocation():
        """Returns the object's location before it was removed."""

    def getObject():
        """Returns the object, or None if the object is unavailable."""
