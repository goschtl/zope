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
$Id: HubEvent.py,v 1.2 2002/10/03 20:53:22 jim Exp $
"""

__metaclass__ = type

from IHubEvent import IObjectRegisteredHubEvent
from IHubEvent import IObjectAddedHubEvent
from IHubEvent import IObjectUnregisteredHubEvent
from IHubEvent import IObjectModifiedHubEvent
from IHubEvent import IObjectMovedHubEvent
from IHubEvent import IObjectRemovedHubEvent

class HubEvent:
    """Convenient mix-in for HubEvents"""

    location = None
    hid = None
    
    def __init__(self, objecthub, hid, location):
        # we keep all three, to avoid unnecessary lookups
        # and to give the objecthub an opportunity to do
        # caching of objects
        self.__objecthub = objecthub
        self.hid = hid
        self.location = location
        
    def __getObject(self):
        if hasattr(self, '_v_object'):
            return self._v_object
        obj = self._v_object = self.__objecthub.getObject(self.hid)
        return obj

    object = property(__getObject)


class ObjectRegisteredHubEvent(HubEvent):
    """An ruid has been freshly created and mapped against an object."""

    __implements__ = IObjectRegisteredHubEvent


class ObjectUnregisteredHubEvent(HubEvent):
    """We are no longer interested in this object."""

    __implements__ = IObjectUnregisteredHubEvent


class ObjectAddedHubEvent(HubEvent):
    """An ruid has been freshly created and mapped against an object.
       Also, implies the object has been newly added."""
    
    __implements__ = IObjectAddedHubEvent
    
    
class ObjectModifiedHubEvent(HubEvent):
    """An object with an ruid has been modified."""
    
    __implements__ = IObjectModifiedHubEvent
    
    
class ObjectMovedHubEvent(HubEvent):
    """An object with an ruid has had its context changed. Typically, this
       means that it has been moved."""
       
    __implements__ = IObjectMovedHubEvent


class ObjectRemovedHubEvent(HubEvent):
    """An object with an ruid has been removed."""

    __implements__ = IObjectRemovedHubEvent

    object = None

    def __init__(self, obj, hid, location):
        self.object = obj
        self.hid = hid
        self.location = location
