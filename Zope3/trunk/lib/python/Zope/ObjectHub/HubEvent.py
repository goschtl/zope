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
$Id: HubEvent.py,v 1.3 2002/10/21 06:14:48 poster Exp $
"""

__metaclass__ = type

from IHubEvent import IObjectRegisteredHubEvent
from IHubEvent import IObjectUnregisteredHubEvent
from IHubEvent import IObjectModifiedHubEvent
from IHubEvent import IObjectMovedHubEvent
from IHubEvent import IObjectRemovedHubEvent
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
        obj = self._v_object = self.__objecthub.getObject(self.hubid)
        return obj

    object = property(__getObject)


class ObjectRegisteredHubEvent(HubEvent):
    """An ruid has been freshly created and mapped against an object."""

    __implements__ = IObjectRegisteredHubEvent


class ObjectUnregisteredHubEvent(HubEvent):
    """We are no longer interested in this object."""

    __implements__ = IObjectUnregisteredHubEvent
    
    # XXX __getObject is *not* implemented in a safe way for this
    # event, because the hubid-to-object mapping in the object hub may
    # have already been deleted.  However, I am more concerned about the
    # local version and will merely mark this as an issue.  In the
    # global object hub I have merely made the deletion happen *after*
    # the event notify.  (We cannot use traverse for these events
    # because that is a Zope-specific capability, in App.)
    
    
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
