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
$Id: ObjectHub.py,v 1.6 2002/07/07 20:32:32 stevea Exp $
"""

from IObjectHub import IObjectHub
from Zope.Event.IObjectEvent import IObjectEvent, IObjectAddedEvent, IObjectModifiedEvent
from Zope.Event.IObjectEvent import IObjectRemovedEvent, IObjectMovedEvent
from Zope.Event.IEvent import IEvent
from Zope.Event.EventChannel import EventChannel
from RuidObjectEvent import RuidObjectRegisteredEvent
from RuidObjectEvent import RuidObjectUnregisteredEvent
from RuidObjectEvent import RuidObjectAddedEvent
from RuidObjectEvent import RuidObjectModifiedEvent
from RuidObjectEvent import RuidObjectContextChangedEvent
from RuidObjectEvent import RuidObjectRemovedEvent
from IRuidObjectEvent import IRuidObjectEvent

from Zope.Exceptions import NotFoundError
from Persistence import Persistent
from Interface.Implements import objectImplements
from types import StringTypes
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

class ObjectHub(Persistent):

    __implements__ =  IObjectHub

    def __init__(self):
        self.__ruid_to_location = IOBTree()
        self.__location_to_ruid = OIBTree()
        self.__eventchannel = EventChannel()
        
    _clear = __init__


    ############################################################
    # Implementation methods for interface
    # Zope.ObjectHub.IObjectHub

    def subscribe(self, subscriber, event_type=IEvent, filter=None):
        '''See interface ISubscribable'''
        self.__eventchannel.subscribe(subscriber, event_type, filter)

    def unsubscribe(self, subscriber, event_type=None, filter=None):
        '''See interface ISubscribable'''
        self.__eventchannel.unsubscribe(subscriber, event_type, filter)
    
    def listSubscriptions(self, subscriber, event_type=None):
        "See interface ISubscribable"
        return self.__eventchannel.listSubscriptions(subscriber, event_type)

    def notify(self, event):
        '''See interface ISubscriber'''
        if IRuidObjectEvent.isImplementedBy(event):
            self.__eventchannel.notify(event)
            return

        if IObjectEvent.isImplementedBy(event):
            self.__eventchannel.notify(event)
            
            if IObjectMovedEvent.isImplementedBy(event):
                canonical_location = locationAsUnicode(event.getFromLocation())
                ruid = self._lookupRuid(canonical_location)
                if ruid is not None:
                    self._objectMoved(event.getFromLocation(),
                                      event.getLocation())
                return
                
            canonical_location = locationAsUnicode(event.getLocation())
            ruid = self._lookupRuid(canonical_location)
            if ruid is not None:
                if IObjectAddedEvent.isImplementedBy(event): 
                    self._objectAdded(canonical_location, ruid)
                    
                elif IObjectModifiedEvent.isImplementedBy(event):
                    self._objectModified(canonical_location, ruid)
                                      
                elif IObjectRemovedEvent.isImplementedBy(event):
                    self._objectRemoved(canonical_location, ruid, event.getObject())
                

        # otherwise, ignore the event

    def lookupRuid(self, location):
        '''See interface IObjectHub'''
        ruid = self._lookupRuid(location)
        if ruid is None:
            raise NotFoundError, locationAsUnicode(location)
        else:
            return ruid
    
    def lookupLocation(self, ruid):
        '''See interface IObjectHub'''
        try:
            return self.__ruid_to_location[ruid]
        except KeyError:
            raise NotFoundError, ruid
        
    def getObject(self, ruid):
        '''See interface IObjectHub'''
        location = self.lookupLocation(ruid)
        adapter = getAdapter(object, ITraverser)
        return adapter.traverse(location)

    def register(self, location):
        '''See interface IObjectHub'''
        canonical_location=locationAsUnicode(location)
        if location[0] != u'/':
            raise ValueError, "Location must be absolute"
        ruid = self._registerObject(canonical_location)

        # send out to plugins IRuidObjectRegisteredEvent
        event = RuidObjectRegisteredEvent(
            self, 
            ruid,
            canonical_location)
        self.__eventchannel.notify(event)
        return ruid

    def unregister(self, ruid_or_location):
        '''See interface IObjectHub'''
        if type(ruid_or_location) is int:
            canonical_location=self.lookupLocation(ruid_or_location)
        else:
            canonical_location=locationAsUnicode(ruid_or_location)
        ruid = self._unregisterObject(canonical_location)
        if ruid is None:
            raise NotFoundError, 'location %s is not in object hub' % \
                canonical_location
        event = RuidObjectUnregisteredEvent(
            self, 
            ruid,
            canonical_location)
        self.__eventchannel.notify(event)
        
    #
    ############################################################

    def _generateRuid(self, location):
        index=getattr(self, '_v_nextid', 0)
        if index%4000 == 0: index = randid()
        ruid_to_location=self.__ruid_to_location
        while not ruid_to_location.insert(index, location):
            index=randid()
        self._v_nextid=index+1
        return index

    def _lookupRuid(self, location):
        canonical_location = locationAsUnicode(location) 
        return self.__location_to_ruid.get(canonical_location, None)

    def _registerObject(self, canonical_location):
        location_to_ruid = self.__location_to_ruid
        if location_to_ruid.has_key(canonical_location):
            raise ObjectHubError, 'location %s already in object hub' % \
                canonical_location
        ruid = self._generateRuid(canonical_location)
        location_to_ruid[canonical_location] = ruid
        return ruid

    def _objectAdded(self, canonical_location, ruid):
        # send out to plugins IRuidObjectAddedEvent
        event = RuidObjectAddedEvent(
            self, 
            ruid,
            canonical_location)
        self.__eventchannel.notify(event)
    
    def _objectModified(self, canonical_location, ruid):
        # send out to plugins IRuidObjectModifiedEvent
        event = RuidObjectModifiedEvent(
            self, 
            ruid,
            canonical_location)
        self.__eventchannel.notify(event)
        
    
    def _objectMoved(self, old_location, new_location):
        location_to_ruid = self.__location_to_ruid
        canonical_location = locationAsUnicode(old_location)
        canonical_new_location = locationAsUnicode(new_location)
        if location_to_ruid.has_key(canonical_new_location):
            raise ObjectHubError(
                'Cannot move to location %s, '
                'as there is already something there'
                % canonical_new_location)
        if not location_to_ruid.has_key(canonical_location):
            # we're not interested in this event
            return

        ruid = location_to_ruid[canonical_location]
        del location_to_ruid[canonical_location]
        location_to_ruid[canonical_new_location] = ruid
        self.__ruid_to_location[ruid] = canonical_new_location
        
        # send out to plugins IRuidObjectContextChangedEvent
        event = RuidObjectContextChangedEvent(
            self, 
            ruid,
            canonical_new_location)
        self.__eventchannel.notify(event)

    def _unregisterObject(self, canonical_location):
        location_to_ruid = self.__location_to_ruid
        ruid_to_location = self.__ruid_to_location
        try:
            ruid = location_to_ruid[canonical_location]
        except KeyError:
            # we don't know about this location, so we
            # just return None 
            return 
        else:
            del ruid_to_location[ruid]
            del location_to_ruid[canonical_location]
            return ruid
        
            
    def _objectRemoved(self, canonical_location, ruid, obj):
            
        # send out to plugins IRuidObjectRemovedEvent
        event = RuidObjectRemovedEvent(
            obj,
            ruid,
            canonical_location)
        self.__eventchannel.notify(event)
