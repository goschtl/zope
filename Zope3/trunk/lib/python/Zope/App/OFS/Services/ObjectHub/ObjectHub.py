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
$Id: ObjectHub.py,v 1.1 2002/10/30 03:47:47 poster Exp $
"""

from Zope.App.OFS.Services.LocalEventService.LocalServiceSubscribable \
     import LocalServiceSubscribable
from Zope.App.OFS.Services.LocalEventService.ProtoServiceEventChannel \
     import ProtoServiceEventChannel

from IObjectHub import IObjectHub, ObjectHubError
from HubEvent import ObjectRegisteredHubEvent
from HubEvent import ObjectUnregisteredHubEvent
from HubEvent import ObjectModifiedHubEvent
from HubEvent import ObjectMovedHubEvent
from HubEvent import ObjectRemovedHubEvent
from IHubEvent import IHubEvent

from Zope.Exceptions import NotFoundError

from Zope.Event.IObjectEvent import IObjectRemovedEvent, IObjectEvent
from Zope.Event.IObjectEvent import IObjectMovedEvent, IObjectAddedEvent
from Zope.Event.IObjectEvent import IObjectModifiedEvent

from Persistence.BTrees.IOBTree import IOBTree
from Persistence.BTrees.OIBTree import OIBTree
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import isWrapper
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.App.Traversing import getPhysicalPathString
from Zope.App.Traversing import locationAsUnicode
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.ComponentArchitecture import getAdapter

import random
def randid():
    # Return a random number between -2*10**9 and 2*10**9, but not 0.
    abs = random.randrange(1, 2000000001)
    if random.random() < 0.5:
        return -abs
    else:
        return abs

class ObjectHub(ProtoServiceEventChannel):
    
    # this implementation makes the decision to not interact with any
    # object hubs above it: it is a world unto itself, as far as it is 
    # concerned, and if it doesn't know how to do something, it won't
    # ask anything else to try.  Everything else is YAGNI for now.
    
    __implements__ = (
        IObjectHub,
        ProtoServiceEventChannel.__implements__)

    def __init__(self):
        ProtoServiceEventChannel.__init__(self)
        self.__hubid_to_location = IOBTree()
        self.__location_to_hubid = OIBTree()
    
    # XXX this is copied because of some context method problems
    # with moving LocalEventChannel.notify to this _notify via a simple
    # assignment, i.e. _notify = LocalEventChannel.notify
    def _notify(clean_self, wrapped_self, event):
        
        subscriptionses = clean_self.subscriptionsForEvent(event)
        # that's a non-interface shortcut for
        # subscriptionses = clean_self._registry.getAllForObject(event)

        for subscriptions in subscriptionses:
            
            for subscriber, filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                ContextWrapper(subscriber, wrapped_self).notify(event)

    def notify(wrapped_self, event):
        '''See interface ISubscriber'''
        clean_self = removeAllProxies(wrapped_self)
        clean_self._notify(wrapped_self, event)
        if IObjectEvent.isImplementedBy(event):
            # generate NotificationHubEvents only if object is known
            # ie registered
            if IObjectMovedEvent.isImplementedBy(event):
                canonical_location = locationAsUnicode(event.fromLocation)
                hubid = clean_self._lookupHubId(canonical_location)
                if hubid is not None:
                    canonical_new_location = locationAsUnicode(
                        event.location)
                    location_to_hubid = clean_self.__location_to_hubid
                    if location_to_hubid.has_key(canonical_new_location):
                        raise ObjectHubError(
                            'Cannot move to location %s, '
                            'as there is already something there'
                            % canonical_new_location)
                    hubid = location_to_hubid[canonical_location]
                    del location_to_hubid[canonical_location]
                    location_to_hubid[canonical_new_location] = hubid
                    clean_self.__hubid_to_location[hubid] = (
                        canonical_new_location)
                    # send out IObjectMovedHubEvent to plugins
                    event = ObjectMovedHubEvent(
                        wrapped_self, 
                        hubid,
                        canonical_location,
                        canonical_new_location,
                        event.object)
                    clean_self._notify(wrapped_self, event)
            
            else: 
                
                canonical_location = locationAsUnicode(event.location)
                hubid = clean_self._lookupHubId(canonical_location)
                if hubid is not None:
                    
                    if IObjectModifiedEvent.isImplementedBy(event):
                        # send out IObjectModifiedHubEvent to plugins
                        event = ObjectModifiedHubEvent(
                            wrapped_self, 
                            hubid,
                            canonical_location,
                            event.object)
                        clean_self._notify(wrapped_self, event)

                    elif IObjectRemovedEvent.isImplementedBy(event):
                        del clean_self.__hubid_to_location[hubid]
                        del clean_self.__location_to_hubid[canonical_location]
                        # send out IObjectRemovedHubEvent to plugins
                        event = ObjectRemovedHubEvent(
                            event.object,
                            hubid,
                            canonical_location,
                            event.object)
                        clean_self._notify(wrapped_self, event)
    
    notify = ContextMethod(notify)

    def getHubId(self, location):
        '''See interface ILocalObjectHub'''
        if isWrapper(location):
            location = getPhysicalPathString(location)
        hubid = self._lookupHubId(location)
        if hubid is None:
            raise NotFoundError(locationAsUnicode(location))
        else:
            return hubid
    
    def getLocation(self, hubid):
        '''See interface IObjectHub'''
        try:
            return self.__hubid_to_location[hubid]
        except KeyError:
            raise NotFoundError(hubid)
    
    def getObject(self, hubid):
        '''See interface IObjectHub'''
        location = self.getLocation(hubid)
        adapter = getAdapter(self, ITraverser)
        return adapter.traverse(location)
    getObject = ContextMethod(getObject)
    
    def register(wrapped_self, location):
        '''See interface ILocalObjectHub'''
        clean_self = removeAllProxies(wrapped_self)
        if isWrapper(location):
            obj = location
            location = getPhysicalPathString(location)
        else:
            obj = None
        canonical_location=locationAsUnicode(location)
        if not location.startswith(u'/'):
            raise ValueError("Location must be absolute")
        location_to_hubid = clean_self.__location_to_hubid
        if location_to_hubid.has_key(canonical_location):
            raise ObjectHubError(
                'location %s already in object hub' % 
                canonical_location)
        hubid = clean_self._generateHubId(canonical_location)
        location_to_hubid[canonical_location] = hubid

        # send out IObjectRegisteredHubEvent to plugins
        event = ObjectRegisteredHubEvent(
            wrapped_self, 
            hubid,
            canonical_location,
            obj)
        clean_self._notify(wrapped_self, event)
        return hubid
    
    register = ContextMethod(register)
    
    def unregister(wrapped_self, location):
        '''See interface ILocalObjectHub'''
        clean_self = removeAllProxies(wrapped_self)
        if isWrapper(location):
            location = getPhysicalPathString(location)
        elif isinstance(location, int):
            canonical_location=clean_self.getLocation(location)
        else:
            canonical_location=locationAsUnicode(location)
        location_to_hubid = clean_self.__location_to_hubid
        hubid_to_location = clean_self.__hubid_to_location
        try:
            hubid = location_to_hubid[canonical_location]
        except KeyError:
            raise NotFoundError, 'location %s is not in object hub' % \
                canonical_location
        else:
            del hubid_to_location[hubid]
            del location_to_hubid[canonical_location]
            
            # send out IObjectUnregisteredHubEvent to plugins
            event = ObjectUnregisteredHubEvent(
                wrapped_self, 
                hubid,
                canonical_location)
            clean_self._notify(wrapped_self, event)
    
    unregister = ContextMethod(unregister)
    
    ############################################################

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
