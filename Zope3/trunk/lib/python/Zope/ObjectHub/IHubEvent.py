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
$Id: IHubEvent.py,v 1.4 2002/10/21 06:14:48 poster Exp $
"""
from Zope.Event.IEvent import IEvent
from Interface.Attribute import Attribute

class IHubEvent(IEvent):
    """Internal Object Hub Event : something has happened to an object for
       which there is a hub id.
       A hub id is a way of refering to an object independent of location.
    """

    object = Attribute("The subject of the event.")

    hubid = Attribute("the object's hub-unique id")

    location = Attribute("An optional object location.")
   

class IRegistrationHubEvent(IHubEvent):
    """The hub registration status of an object has changed
    """


class IObjectRegisteredHubEvent(IRegistrationHubEvent):
    """A hub id has been freshly created and mapped against an object."""


class IObjectUnregisteredHubEvent(IRegistrationHubEvent):
    """We are no longer interested in this object."""
    
    
class IObjectModifiedHubEvent(IHubEvent):
    """An object with a hub id has been modified."""
    
    
class IObjectMovedHubEvent(IHubEvent):
    """An object with a hub id has had its context changed. Typically, this
       means that it has been moved."""

    fromLocation = Attribute("The old location for the object.")


class IObjectRemovedHubEvent(IObjectUnregisteredHubEvent):
    """An object with a hub id has been removed and unregistered."""
