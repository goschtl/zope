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
$Id: LocalObjectHub.py,v 1.1 2002/10/21 06:14:46 poster Exp $
"""

from Zope.App.OFS.Services.LocalEventService.LocalServiceSubscribable \
     import LocalServiceSubscribable
from Zope.App.OFS.Services.LocalEventService.ProtoServiceEventChannel \
     import ProtoServiceEventChannel
from Zope.ObjectHub.ObjectHub import ObjectHubError, randid
from Zope.ObjectHub.IObjectHub import IObjectHub
from LocalHubEvent import ObjectRegisteredHubEvent
from LocalHubEvent import ObjectUnregisteredHubEvent
from LocalHubEvent import ObjectModifiedHubEvent
from LocalHubEvent import ObjectMovedHubEvent
from LocalHubEvent import ObjectRemovedHubEvent
from Zope.ObjectHub.IHubEvent import IHubEvent

from Zope.Exceptions import NotFoundError

from Zope.Event.IObjectEvent import \
    IObjectEvent, IObjectAddedEvent, IObjectModifiedEvent
from Zope.Event.IObjectEvent import IObjectRemovedEvent, IObjectMovedEvent

from Persistence.BTrees.IOBTree import IOBTree
from Persistence.BTrees.OIBTree import OIBTree
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import isWrapper
from Zope.App.Traversing import getPhysicalPathString
from Zope.App.Traversing import locationAsUnicode
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.Proxy.ContextWrapper import ContextWrapper

class ILocalObjectHub(IObjectHub): # XXX also put in proto stuff here?
    
    def lookupHubId(wrappedObj_or_location):
        """like IObjectHub.lookupHubId but also accepts wrapped object"""
    
    def register(wrappedObj_or_location):
        """like IObjectHub.register but also accepts wrapped object"""
    
    def unregister(wrappedObj_or_location_or_hubid):
        """like IObjectHub.unregister but also accepts wrapped object"""

class LocalObjectHub(ProtoServiceEventChannel):
    
    # this implementation makes the decision to not interact with any
    # object hubs above it: it is a world unto itself, as far as it is 
    # concerned, and if it doesn't know how to do something, it won't
    # ask anything else to try.  Everything else is YAGNI for now.
    
    __implements__ = (
        ILocalObjectHub,
        ProtoServiceEventChannel.__implements__)

    def __init__(self):
        ProtoServiceEventChannel.__init__(self)
        self.__hubid_to_location = IOBTree()
        self.__location_to_hubid = OIBTree()
    
    def _notify(clean_self, wrapped_self, event):
        
        subscriptionses = clean_self.subscriptionsForEvent(event)
        # that's a non-interface shortcut for
        # subscriptionses = clean_self._registry.getAllForObject(event)

        for subscriptions in subscriptionses:
            
            for subscriber,filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                ContextWrapper(subscriber, wrapped_self).notify(event)

    # notify has to have a minor overhaul from the placeless version
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
                        canonical_new_location)
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
                            canonical_location)
                        clean_self._notify(wrapped_self, event)

                    elif IObjectRemovedEvent.isImplementedBy(event):
                        del clean_self.__hubid_to_location[hubid]
                        del clean_self.__location_to_hubid[canonical_location]
                        # send out IObjectRemovedHubEvent to plugins
                        event = ObjectRemovedHubEvent(
                            event.object,
                            hubid,
                            canonical_location)
                        clean_self._notify(wrapped_self, event)
    
    notify = ContextMethod(notify)

    # lookupHubId just has new ability to take an object
    def lookupHubId(self, location):
        '''See interface ILocalObjectHub'''
        if isWrapper(location):
            location = getPhysicalPathString(location)
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
    getObject = ContextMethod(getObject)
    
    # we must give register an overhaul also
    def register(wrapped_self, location):
        '''See interface ILocalObjectHub'''
        clean_self = removeAllProxies(wrapped_self)
        if isWrapper(location):
            location = getPhysicalPathString(location)
        canonical_location=locationAsUnicode(location)
        if location[0] != u'/':
            raise ValueError, "Location must be absolute"
        location_to_hubid = clean_self.__location_to_hubid
        if location_to_hubid.has_key(canonical_location):
            raise ObjectHubError, 'location %s already in object hub' % \
                canonical_location
        hubid = clean_self._generateHubId(canonical_location)
        location_to_hubid[canonical_location] = hubid

        # send out IObjectRegisteredHubEvent to plugins
        event = ObjectRegisteredHubEvent(
            wrapped_self, 
            hubid,
            canonical_location)
        clean_self._notify(wrapped_self, event)
        return hubid
    
    register = ContextMethod(register)
    
    # as well as unregister
    def unregister(wrapped_self, location):
        '''See interface ILocalObjectHub'''
        clean_self = removeAllProxies(wrapped_self)
        if isWrapper(location):
            location = getPhysicalPathString(location)
        elif isinstance(location, int):
            canonical_location=clean_self.lookupLocation(location)
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
    
    # we use two helpers copied from the ObjectHub base class:

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
    
    # Not sure about plugins yet--will see what the response to my add
    # and remove emails are
    