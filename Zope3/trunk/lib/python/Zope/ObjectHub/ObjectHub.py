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
$Id: ObjectHub.py,v 1.3 2002/06/24 15:07:03 dannu Exp $
"""

from IObjectHub import IObjectHub
from Zope.Event.IObjectEvent import IObjectAddedEvent, IObjectModifiedEvent
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
        if IObjectAddedEvent.isImplementedBy(event):
            self._objectAdded(event.getLocation())
            
        elif IObjectModifiedEvent.isImplementedBy(event):
            self._objectModified(event.getLocation())
            
        elif IObjectMovedEvent.isImplementedBy(event):
            self._objectMoved(event.getFromLocation(),
                              event.getLocation())
                              
        elif IObjectRemovedEvent.isImplementedBy(event):
            self._objectRemoved(event.getLocation(), event.getObject())
        
        elif IRuidObjectEvent.isImplementedBy(event):
            self.__eventchannel.notify(event)

        # otherwise, ignore the event

    def lookupRuid(self, location):
        '''See interface IObjectHub'''
        try:
            return self.__location_to_ruid[self._canonical(location)]
        except KeyError:
            raise NotFoundError, self._canonical(location)
    
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

    def _canonical(location):
        if not isinstance(location, StringTypes):
            location='/'.join(location)
        # URIs are ascii, right?
        return str(location)
        
    _canonical=staticmethod(_canonical)

    def _objectAdded(self, location):
        canonical_location = self._canonical(location)
        
        location_to_ruid = self.__location_to_ruid
                
        if location_to_ruid.has_key(canonical_location):
            raise ObjectHubError, 'location %s already in object hub' % \
                canonical_location
        ruid = self._generateRuid(canonical_location)
        location_to_ruid[canonical_location] = ruid
        
        # send out to plugins IRuidObjectAddedEvent
        event = RuidObjectAddedEvent(
            self, 
            ruid,
            canonical_location)
        self.__eventchannel.notify(event)
        
    
    def _objectModified(self, location):
        location_to_ruid = self.__location_to_ruid
        canonical_location = self._canonical(location)
        if not location_to_ruid.has_key(canonical_location):
            # we're not interested in this event
            return
            
        # send out to plugins IRuidObjectModifiedEvent
        event = RuidObjectModifiedEvent(
            self, 
            location_to_ruid[canonical_location],
            canonical_location)
        self.__eventchannel.notify(event)
        
    
    def _objectMoved(self, old_location, new_location):
        location_to_ruid = self.__location_to_ruid
        canonical_location = self._canonical(old_location)
        canonical_new_location = self._canonical(new_location)
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

            
    def _objectRemoved(self, location, obj):
        location_to_ruid = self.__location_to_ruid
        ruid_to_location = self.__ruid_to_location
        canonical_location = self._canonical(location)
        try:
            ruid = location_to_ruid[canonical_location]
        except KeyError:
            # we don't know about this location, so we
            # can ignore this event
            return
            
        del ruid_to_location[ruid]
        del location_to_ruid[canonical_location]
            
        # send out to plugins IRuidObjectRemovedEvent
        event = RuidObjectRemovedEvent(
            obj,
            ruid,
            canonical_location)
        self.__eventchannel.notify(event)
