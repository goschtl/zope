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
$Id: IObjectEvent.py,v 1.3 2002/09/03 20:12:46 jim Exp $
"""

from IEvent import IEvent

class IObjectEvent(IEvent):
    """Something has happened to an object.

    The object that generated this event is not necessarily the object
    refered to by getLocation.
    """

    def getLocation():        
        """returns the object location."""

class IObjectAddedEvent(IObjectEvent):
    """An object has been added to a container."""

    def getLocation():        
        """Returns the object location.

        This is the location after it has been added to the container"""

class IObjectModifiedEvent(IObjectEvent):
    """An object has been modified"""

class IObjectRemovedEvent(IObjectEvent):
    """An object has been removed from a container"""
    
    def getLocation():
        """location of the object before it was removed"""
        
    def getObject():
        """the object that was removed"""

class IObjectMovedEvent(IObjectEvent):
    """An object has been moved"""

    def getFromLocation():
        """location of the object before it was moved"""

    def getLocation():
        """location of the object after it was moved"""
