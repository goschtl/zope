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
$Id: ObjectHub.py,v 1.10 2002/10/21 06:14:48 poster Exp $
"""

from IObjectHub import IObjectHub
from Zope.Event.IObjectEvent import \
    IObjectEvent, IObjectAddedEvent, IObjectModifiedEvent
from Zope.Event.IObjectEvent import IObjectRemovedEvent, IObjectMovedEvent
from Zope.Event.IEvent import IEvent
from Zope.Event.EventChannel import EventChannel
from HubEvent import ObjectRegisteredHubEvent
from HubEvent import ObjectUnregisteredHubEvent
from HubEvent import ObjectModifiedHubEvent
from HubEvent import ObjectMovedHubEvent
from HubEvent import ObjectRemovedHubEvent
from IHubEvent import IHubEvent

from Zope.Exceptions import NotFoundError
from Persistence import Persistent
from Persistence.BTrees.IOBTree import IOBTree
from Persistence.BTrees.OIBTree import OIBTree

from Zope.App.Traversing import locationAsUnicode

from Zope.App.Traversing.ITraverser import ITraverser
from Zope.ComponentArchitecture import getAdapter

import random
def randid():
    # Return a random number between -2*10**9 and 2*10**9, but not 0.
    abs = random.randrange(1, 2000000001)
    if random.random() < 0.5:
        return -abs
    else:
        return abs

class ObjectHubError(Exception):
    pass

class ObjectHub(EventChannel, Persistent):

    __implements__ =  IObjectHub

    def __init__(self):
        EventChannel.__init__(self)
        self.__hubid_to_location = IOBTree()
        self.__location_to_hubid = OIBTree()
        
    _clear = __init__


    ############################################################
    # Implementation methods for interface
    # Zope.ObjectHub.IObjectHub

    def notify(self, event):
        '''See interface ISubscriber'''
        self._notify(event)

        if IObjectEvent.isImplementedBy(event):
            # generate NotificationHubEvents only if object is known
            # ie registered  
            if IObjectMovedEvent.isImplementedBy(event):
                canonical_location = locationAsUnicode(event.fromLocation)
                hubid = self._lookupHubId(canonical_location)
                if hubid is not None:
                    self._objectMoved(event.fromLocation,
                                      event.location)
                return
            
            canonical_location = locationAsUnicode(event.location)
            hubid = self._lookupHubId(canonical_location)
            if hubid is not None:
                    
                if IObjectModifiedEvent.isImplementedBy(event):
                    self._objectModified(canonical_location, hubid)
                
                elif IObjectRemovedEvent.isImplementedBy(event):
                    self._objectRemoved(canonical_location,
                                        hubid,
                                        event.object)
        # otherwise, ignore the event

    def lookupHubId(self, location):
        '''See interface IObjectHub'''
        hubid = self._lookupHubId(location)
        if hubid is None:
            raise NotFoundError, locationAsUnicode(location)
        else:
            return hubid
    
    def lookupLocation(self, hubid):
        '''See interface IObjectHub'''
        try:
            return self.__hubid_to_location[hubid]
        except KeyError:
            raise NotFoundError, hubid
        
    def getObject(self, hubid):
        '''See interface IObjectHub'''
        location = self.lookupLocation(hubid)
        adapter = getAdapter(self, ITraverser)
        return adapter.traverse(location)

    def register(self, location):
        '''See interface IObjectHub'''
        canonical_location=locationAsUnicode(location)
        if location[0] != u'/':
            raise ValueError, "Location must be absolute"
        hubid = self._registerObject(canonical_location)
        return hubid

    def unregister(self, hubid_or_location):
        '''See interface IObjectHub'''
        if type(hubid_or_location) is int:
            canonical_location=self.lookupLocation(hubid_or_location)
        else:
            canonical_location=locationAsUnicode(hubid_or_location)
        hubid = self._unregisterObject(canonical_location)
        if hubid is None:
            raise NotFoundError, 'location %s is not in object hub' % \
                canonical_location
  
    #
    ############################################################
    
    _notify = EventChannel.notify # this is a plug so we can reuse
    # almost the entirety of this code for the local version of the
    # ObjectHub (Zope.App.OFS.Services.ObjectHub.ObjectHub)

    def _generateHubId(self, location):
        index=getattr(self, '_v_nextid', 0)
        if index%4000 == 0: index = randid()
        hubid_to_location=self.__hubid_to_location
        while not hubid_to_location.insert(index, location):
            index=randid()
        self._v_nextid=index+1
        return index

    def _lookupHubId(self, location):
        canonical_location = locationAsUnicode(location) 
        return self.__location_to_hubid.get(canonical_location, None)

    def _registerObject(self, canonical_location):
        location_to_hubid = self.__location_to_hubid
        if location_to_hubid.has_key(canonical_location):
            raise ObjectHubError, 'location %s already in object hub' % \
                canonical_location
        hubid = self._generateHubId(canonical_location)
        location_to_hubid[canonical_location] = hubid

        # send out IObjectRegisteredHubEvent to plugins
        event = ObjectRegisteredHubEvent(
            self, 
            hubid,
            canonical_location)
        self._notify(event)
        return hubid

    # see comment in notify
    #def _objectAdded(self, canonical_location, hubid):
    #    # send out IObjectAddedHubEvent to plugins
    #    event = ObjectAddedHubEvent(
    #        self, 
    #        hubid,
    #        canonical_location)
    #    self._notify(event)
    
    def _objectModified(self, canonical_location, hubid):
        # send out IObjectModifiedHubEvent to plugins
        event = ObjectModifiedHubEvent(
            self, 
            hubid,
            canonical_location)
        self._notify(event)
    
    def _objectMoved(self, old_location, new_location):
        location_to_hubid = self.__location_to_hubid
        canonical_location = locationAsUnicode(old_location)
        canonical_new_location = locationAsUnicode(new_location)
        if location_to_hubid.has_key(canonical_new_location):
            raise ObjectHubError(
                'Cannot move to location %s, '
                'as there is already something there'
                % canonical_new_location)
        hubid = location_to_hubid[canonical_location]
        del location_to_hubid[canonical_location]
        location_to_hubid[canonical_new_location] = hubid
        self.__hubid_to_location[hubid] = canonical_new_location
        # send out IObjectMovedHubEvent to plugins
        event = ObjectMovedHubEvent(
            self, 
            hubid,
            canonical_new_location)
        self._notify(event)

    def _unregisterObject(self, canonical_location):
        location_to_hubid = self.__location_to_hubid
        hubid_to_location = self.__hubid_to_location
        try:
            hubid = location_to_hubid[canonical_location]
        except KeyError:
            # we don't know about this location, so we
            # just return None 
            return 
        else:
            del hubid_to_location[hubid]
            del location_to_hubid[canonical_location]
            # send out IObjectUnregisteredHubEvent to plugins
            event = ObjectUnregisteredHubEvent(
                self, 
                hubid,
                canonical_location)
            self._notify(event)
            return hubid

    def _objectRemoved(self, canonical_location, hubid, obj):
        # send out IObjectRemovedHubEvent to plugins
        event = ObjectRemovedHubEvent(
            obj,
            hubid,
            canonical_location)
        self._notify(event)
        
        # we would delete the registration first, but it's not safe
        # for the global version--see HubEvent.ObjectUnregisteredHubEvent
        del self.__hubid_to_location[hubid]
        del self.__location_to_hubid[canonical_location]
