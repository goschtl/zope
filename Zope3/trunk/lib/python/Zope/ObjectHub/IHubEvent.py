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
$Id: IHubEvent.py,v 1.1 2002/08/22 17:05:24 gotcha Exp $
"""
from Zope.Event.IEvent import IEvent

class IHubEvent(IEvent):
    """Internal Object Hub Event : something has happened to an object for
       which there is an ruid.
       An ruid is a way of refering to an object independent of location.
    """

    def getRuid():
        """Returns the object's ruid."""
   
    def getLocation():
        """Returns the object's current location."""
   
    def getObject():
        """Returns the object."""
   

class IRegistrationHubEvent(IHubEvent):
    """Some work could be done on registration or deregistration of an object."""


class IObjectRegisteredHubEvent(IRegistrationHubEvent):
    """An ruid has been freshly created and mapped against an object."""


class IObjectUnregisteredHubEvent(IRegistrationHubEvent):
    """We are no longer interested in this object."""


class INotificationHubEvent(IHubEvent):
    """Some work has be done on a registrated object."""


class IObjectAddedHubEvent(INotificationHubEvent):
    """An ruid has been freshly created and mapped against an object.
       Also, implies the object has been newly added."""
    
    
class IObjectModifiedHubEvent(INotificationHubEvent):
    """An object with an ruid has been modified."""
    
    
class IObjectMovedHubEvent(INotificationHubEvent):
    """An object with an ruid has had its context changed. Typically, this
       means that it has been moved."""

   
class IObjectRemovedHubEvent(INotificationHubEvent):
    """An object with an ruid has been removed."""

    def getLocation():
        """Returns the object's location before it was removed."""

    def getObject():
        """Returns the object, or None if the object is unavailable."""
