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
$Id: LocalHubEvent.py,v 1.1 2002/10/21 06:14:46 poster Exp $
"""

__metaclass__ = type

from Zope.ObjectHub.IHubEvent import IObjectRegisteredHubEvent
from Zope.ObjectHub.IHubEvent import IObjectUnregisteredHubEvent
from Zope.ObjectHub.IHubEvent import IObjectModifiedHubEvent
from Zope.ObjectHub.IHubEvent import IObjectMovedHubEvent
from Zope.ObjectHub.IHubEvent import IObjectRemovedHubEvent
from Zope.App.Traversing import traverse

class HubEvent:
    """Convenient mix-in for HubEvents"""

    location = None
    hubid = None
    
    def __init__(self, objecthub, hubid, location):
        # we keep all three, to avoid unnecessary lookups
        # and to give the objecthub an opportunity to do
        # caching of objects
        self.__objecthub = objecthub
        self.hubid = hubid
        self.location = location
        
    def __getObject(self):
        if hasattr(self, '_v_object'):
            return self._v_object
        obj = self._v_object = traverse(
            self.__objecthub, self.location)
        # we use the above instead of the below primarily because
        # the object hub call is not guaranteed to work on an
        # unregistered event; the above also does a bit less work:
        # obj = self._v_object = (self.__objecthub.getObject(self.__hubid)
        # and that, unfortunately, is the only reason why we're not
        # using the Zope.ObjectHub.HubEvent versions of these...
        return obj

    object = property(__getObject)


class ObjectRegisteredHubEvent(HubEvent):
    """An ruid has been freshly created and mapped against an object."""

    __implements__ = IObjectRegisteredHubEvent


class ObjectUnregisteredHubEvent(HubEvent):
    """We are no longer interested in this object."""

    __implements__ = IObjectUnregisteredHubEvent
    
    
class ObjectModifiedHubEvent(HubEvent):
    """An object with an ruid has been modified."""
    
    __implements__ = IObjectModifiedHubEvent
    
    
class ObjectMovedHubEvent(HubEvent):
    """An object with an ruid has had its context changed. Typically, this
       means that it has been moved."""
       
    __implements__ = IObjectMovedHubEvent


class ObjectRemovedHubEvent:
    """An object with an ruid has been removed."""

    __implements__ = IObjectRemovedHubEvent
    # ...which is a subclass of IObjectUnregisteredHubEvent

    def __init__(self, obj, hubid, location):
        self.object = obj
        self.hubid = hubid
        self.location = location
