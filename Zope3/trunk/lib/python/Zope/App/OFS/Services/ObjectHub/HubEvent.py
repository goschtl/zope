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
$Id: HubEvent.py,v 1.1 2002/10/30 03:47:47 poster Exp $
"""

__metaclass__ = type

from IHubEvent import IObjectRegisteredHubEvent
from IHubEvent import IObjectUnregisteredHubEvent
from IHubEvent import IObjectModifiedHubEvent
from IHubEvent import IObjectMovedHubEvent
from IHubEvent import IObjectRemovedHubEvent
from Zope.App.Traversing import traverse
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.ComponentArchitecture import getAdapter

class HubEvent:
    """Convenient mix-in for HubEvents"""

    hub = None
    hubid = None
    # object = None
    # location = None
    
    def __init__(self, hub, hubid, location=None, object=None):
        # we keep all four, to avoid unnecessary lookups
        # and to give the objecthub an opportunity to do
        # caching of objects
        self.hub = hub
        self.hubid = hubid
        self.__object = object
        self.__location = location
        
    def __getObject(self):
        obj = self.__object
        if obj is None:
            obj = self.__object = self.hub.getObject(self.hubid)
        return obj

    object = property(__getObject)
    
    def __getLocation(self):
        loc = self.__location
        if loc is None:
            loc = self.__location = self.hub.getLocation(self.hubid)
        return loc
    
    location = property(__getLocation)


class ObjectRegisteredHubEvent(HubEvent):
    """A hubid has been freshly created and mapped against an object."""

    __implements__ = IObjectRegisteredHubEvent


class ObjectUnregisteredHubEvent:
    """We are no longer interested in this object.
    
    """    

    hub = None
    hubid = None
    # object = None
    location = None
    
    def __init__(self, hub, hubid, location, object=None):
        # location *must* be supplied because the object hub cannot be
        # relied upon to translate an unregistered hubid
        self.hub = hub
        self.hubid = hubid
        self.__object = object
        self.location = location

    __implements__ = IObjectUnregisteredHubEvent
        
    def __getObject(self):
        obj = self.__object
        if obj is None:
            adapter = getAdapter(self.hub, ITraverser)
            obj = self.__object = adapter.traverse(self.location)
        return obj

    object = property(__getObject)
    
    
class ObjectModifiedHubEvent(HubEvent):
    """An object with a hubid has been modified."""
    
    __implements__ = IObjectModifiedHubEvent
    
    
class ObjectMovedHubEvent(HubEvent):
    """An object with a hubid has had its context changed. Typically, this
       means that it has been moved."""
    
    def __init__(self, hub, hubid, fromLocation, location=None, object=None):
        self.fromLocation = fromLocation
        HubEvent.__init__(self, hub, hubid, location, object)
       
    __implements__ = IObjectMovedHubEvent


class ObjectRemovedHubEvent(ObjectUnregisteredHubEvent):
    """An object with a hubid has been removed."""

    __implements__ = IObjectRemovedHubEvent
    # ...which is a subclass of IObjectUnregisteredHubEvent

    hub = None
    hubid = None
    object = None
    location = None
    
    def __init__(self, hub, hubid, location, object):
        # all four *must* be supplied because the object hub cannot be
        # relied upon to translate an unregistered hubid
        self.hub = hub
        self.hubid = hubid
        self.object = object
        self.location = location
