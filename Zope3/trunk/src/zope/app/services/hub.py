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
"""Object hub implementation.

$Id: hub.py,v 1.19 2003/07/13 07:18:23 anthony Exp $
"""

from __future__ import generators

__metaclass__ = type

import random

from zodb.btrees.IOBTree import IOBTree
from zodb.btrees.OIBTree import OIBTree

from zope.app.traversing import getPath, canonicalPath

from zope.component import getAdapter, getService
from zope.exceptions import NotFoundError
from zope.context import ContextMethod
from zope.proxy import removeAllProxies
from zope.app.services.servicenames import EventSubscription

from zope.app.interfaces.traversing import ITraverser
from zope.app.interfaces.event import IObjectRemovedEvent, IObjectEvent
from zope.app.interfaces.event import IObjectMovedEvent, IObjectCreatedEvent
from zope.app.interfaces.event import IObjectModifiedEvent
from zope.app.interfaces.services.hub import IObjectHub, ObjectHubError
from zope.app.services.event import ServiceSubscriberEventChannel
from zope.app.interfaces.services.hub import IObjectRegisteredHubEvent
from zope.app.interfaces.services.hub import IObjectUnregisteredHubEvent
from zope.app.interfaces.services.hub import IObjectModifiedHubEvent
from zope.app.interfaces.services.hub import IObjectMovedHubEvent
from zope.app.interfaces.services.hub import IObjectRemovedHubEvent
from zope.app.interfaces.traversing import ITraverser
from zope.app.interfaces.services.service import ISimpleService
from zope.interface import implements
from zope.app.interfaces.event import ISubscriber
from zope.app.interfaces.event import IObjectAddedEvent
from zope.app.interfaces.content.folder import IFolder
from zope.app.interfaces.traversing import ITraversable
from zope.app.services.servicenames import HubIds
from zope.app.event.objectevent import ObjectAddedEvent

from zope.app.traversing import traverse, traverseName, getPath, getRoot
from zope.app.interfaces.services.hub import ObjectHubError
from zope.app.interfaces.services.hub import ISubscriptionControl
from persistence import Persistent

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
            loc = self.__location = self.hub.getPath(self.hubid)
        return loc

    location = property(__getLocation)


class ObjectRegisteredHubEvent(HubEvent):
    """A hubid has been freshly created and mapped against an object."""

    implements(IObjectRegisteredHubEvent)


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

    implements(IObjectUnregisteredHubEvent)

    def __getObject(self):
        obj = self.__object
        if obj is None:
            adapter = getAdapter(self.hub, ITraverser)
            obj = self.__object = adapter.traverse(self.location)
        return obj

    object = property(__getObject)


class ObjectModifiedHubEvent(HubEvent):
    """An object with a hubid has been modified."""

    implements(IObjectModifiedHubEvent)


class ObjectMovedHubEvent(HubEvent):
    """An object with a hubid has had its context changed. Typically, this
       means that it has been moved."""

    def __init__(self, hub, hubid, fromLocation, location=None, object=None):
        self.fromLocation = fromLocation
        HubEvent.__init__(self, hub, hubid, location, object)

    implements(IObjectMovedHubEvent)


class ObjectRemovedHubEvent(ObjectUnregisteredHubEvent):
    """An object with a hubid has been removed."""

    implements(IObjectRemovedHubEvent)
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


def randid():
    # Return a random number between -2*10**9 and 2*10**9, but not 0.
    abs = random.randrange(1, 2000000001)
    if random.random() < 0.5:
        return -abs
    else:
        return abs

def canonicalSlash(path):
    # Return a canonical path, with a slash appended
    return canonicalPath(path) + u'/'

class ObjectHub(ServiceSubscriberEventChannel):

    # this implementation makes the decision to not interact with any
    # object hubs above it: it is a world unto itself, as far as it is
    # concerned, and if it doesn't know how to do something, it won't
    # ask anything else to try.  Everything else is YAGNI for now.

    implements(IObjectHub, ISimpleService)

    def __init__(self):
        ServiceSubscriberEventChannel.__init__(self)
        # A pathslash is a path with a '/' on the end.
        # int --> unicode pathslash
        self.__hubid_to_path = IOBTree()
        # unicode pathslash --> int
        self.__path_to_hubid = OIBTree()

    def notify(wrapped_self, event):
        '''See interface ISubscriber'''
        clean_self = removeAllProxies(wrapped_self)
        clean_self._notify(wrapped_self, event)
        if IObjectEvent.isImplementedBy(event):
            # generate NotificationHubEvents only if object is known
            # ie registered
            if IObjectMovedEvent.isImplementedBy(event):
                pathslash = canonicalSlash(event.fromLocation)
                hubid = clean_self.__path_to_hubid.get(pathslash)
                if hubid is not None:
                    new_pathslash = canonicalSlash(event.location)
                    path_to_hubid = clean_self.__path_to_hubid
                    if path_to_hubid.has_key(new_pathslash):
                        raise ObjectHubError(
                            'Cannot move to location %s, '
                            'as there is already something there'
                            % new_pathslash[:-1])
                    hubid = path_to_hubid[pathslash]
                    del path_to_hubid[pathslash]
                    path_to_hubid[new_pathslash] = hubid
                    clean_self.__hubid_to_path[hubid] = new_pathslash
                    # send out IObjectMovedHubEvent to plugins
                    event = ObjectMovedHubEvent(
                        wrapped_self, hubid, pathslash[:-1],
                        new_pathslash[:-1], event.object)
                    clean_self._notify(wrapped_self, event)
            elif IObjectCreatedEvent.isImplementedBy(event):
                # a newly created object that has not been added to a
                # container yet has no location. So, we're not interested in
                # it.
                pass
            else:
                pathslash = canonicalSlash(event.location)
                hubid = clean_self.__path_to_hubid.get(pathslash)
                if hubid is not None:
                    if IObjectModifiedEvent.isImplementedBy(event):
                        # send out IObjectModifiedHubEvent to plugins
                        event = ObjectModifiedHubEvent(
                            wrapped_self, hubid, pathslash[:-1], event.object)
                        clean_self._notify(wrapped_self, event)
                    elif IObjectRemovedEvent.isImplementedBy(event):
                        del clean_self.__hubid_to_path[hubid]
                        del clean_self.__path_to_hubid[pathslash]
                        # send out IObjectRemovedHubEvent to plugins
                        event = ObjectRemovedHubEvent(
                            event.object, hubid, pathslash[:-1], event.object)
                        clean_self._notify(wrapped_self, event)
    notify = ContextMethod(notify)

    def getHubId(self, path_or_object):
        '''See interface ILocalObjectHub'''
        if isinstance(path_or_object, (unicode, str)):
            path = path_or_object
        else:
            path = getPath(path_or_object)

        pathslash = canonicalSlash(path)
        hubid = self.__path_to_hubid.get(pathslash)
        if hubid is None:
            raise NotFoundError(path)
        else:
            return hubid

    def getPath(self, hubid):
        '''See interface IObjectHub'''
        try:
            return self.__hubid_to_path[hubid][:-1]
        except KeyError:
            raise NotFoundError(hubid)

    def getObject(wrapped_self, hubid):
        '''See interface IObjectHub'''
        path = wrapped_self.getPath(hubid)
        adapter = getAdapter(wrapped_self, ITraverser)
        return adapter.traverse(path)
    getObject = ContextMethod(getObject)

    def register(wrapped_self, path_or_object):
        '''See interface ILocalObjectHub'''
        clean_self = removeAllProxies(wrapped_self)
        # XXX Need a new unit test for this; previously we tested
        #     whether it's wrapped, which is wrong because the root
        #     isn't wrapped (and it certainly makes sense to want to
        #     register the root).
        if isinstance(path_or_object, (str, unicode)):
            obj = None
            path = path_or_object
        else:
            obj = path_or_object
            path = getPath(path_or_object)

        pathslash = canonicalSlash(path)

        path_to_hubid = clean_self.__path_to_hubid
        if path_to_hubid.has_key(pathslash):
            raise ObjectHubError('path %s already in object hub' % path)
        hubid = clean_self._generateHubId(pathslash)
        path_to_hubid[pathslash] = hubid

        # send out IObjectRegisteredHubEvent to plugins
        event = ObjectRegisteredHubEvent(
            wrapped_self, hubid, pathslash[:-1], obj)
        clean_self._notify(wrapped_self, event)
        return hubid
    register = ContextMethod(register)

    def unregister(wrapped_self, path_or_object_or_hubid):
        '''See interface ILocalObjectHub'''
        clean_self = removeAllProxies(wrapped_self)
        if isinstance(path_or_object_or_hubid, (unicode, str)):
            path = canonicalPath(path_or_object_or_hubid)
        elif isinstance(path_or_object_or_hubid, int):
            path = clean_self.getPath(path_or_object_or_hubid)
        else:
            path = getPath(path_or_object_or_hubid)

        pathslash = canonicalSlash(path)

        path_to_hubid = clean_self.__path_to_hubid
        hubid_to_path = clean_self.__hubid_to_path
        try:
            hubid = path_to_hubid[pathslash]
        except KeyError:
            raise NotFoundError('path %s is not in object hub' % path)
        else:
            del hubid_to_path[hubid]
            del path_to_hubid[pathslash]

            # send out IObjectUnregisteredHubEvent to plugins
            event = ObjectUnregisteredHubEvent(
                wrapped_self, hubid, pathslash[:-1])
            clean_self._notify(wrapped_self, event)
    unregister = ContextMethod(unregister)

    def numRegistrations(self):
        """See interface IObjectHub"""
        # The hubid<-->path mapping should be the same size.
        # The IOBTree of hubid-->path might be faster to find the
        # size of, as the keys are ints. But, I haven't tested that.
        # assert len(self.__hubid_to_path)==len(self.__path_to_hubid)
        return len(self.__hubid_to_path)

    def iterRegistrations(self, path=u'/'):
        """See interface IObjectHub"""
        # or unicodes. So, get a canonical path first of all.
        pathslash = canonicalSlash(path)
        if pathslash == u'//':
            # Optimisation when we're asked for all the registered objects.
            # Returns an IOBTreeItems object.
            for pathslash, hubId in self.__path_to_hubid.iteritems():
                yield pathslash[:-1], hubId

        else:
            # For a search /foo/bar, constrain the paths returned to those
            # between /foo/bar/ and /foo/bar0, excluding /foo/bar0.
            # chr(ord('/')+1) == '0'
            for pathslash, hubId in self.__path_to_hubid.iteritems(
                min=pathslash, max=pathslash[:-1]+u'0', excludemax=True):
                yield pathslash[:-1], hubId

    def iterObjectRegistrations(wrapped_self):
        """See interface IHubEventChannel"""
        traverser = getAdapter(wrapped_self, ITraverser)
        for path, hubId in wrapped_self.iterRegistrations():
            yield (path, hubId, traverser.traverse(path))
    iterObjectRegistrations = ContextMethod(iterObjectRegistrations)

    ############################################################

    def _generateHubId(self, pathslash):
        index = getattr(self, '_v_nextid', 0)
        if index%4000 == 0:
            index = randid()
        hubid_to_path = self.__hubid_to_path
        while not hubid_to_path.insert(index, pathslash):
            index = randid()
        self._v_nextid = index + 1
        return index


"""A simple-minded registration object.

In order for the ObjectHub to actually serve a purpose, objects 
need to be registered with the object hub.  A real site should 
define a policy for when objects are to be registered.  This 
particular implementation subscribes to IObjectAddedEvent events 
from the event service, and registers absolutely everything. A 
site that wishes to implement a different subscription policy
can write their own Registration object (at the moment this seems
somewhat yagni to us).

It also has a way of registering all pre-existing objects.

This code was originally implemented for the index package, but it's
very much ObjectHub-specific for now. 
"""


class Registration(Persistent):

    implements(ISubscriptionControl, ISubscriber)

    def notify(wrapped_self, event):
        """An event occured. Perhaps register this object with the hub."""

        # XXX quick hack to make sure we *only* register on add events
        # and not on extending events like move events.
        # We still need to sort out move semantics. We certainly don't
        # have it correct now.

        if event.__class__ is ObjectAddedEvent:
            hub = getService(wrapped_self, HubIds)
            wrapped_self._registerObject(event.location, hub)
    notify = ContextMethod(notify)

    currentlySubscribed = False # Default subscription state

    def subscribe(wrapped_self):
        if wrapped_self.currentlySubscribed:
            raise RuntimeError, "already subscribed; please unsubscribe first"
        # we subscribe to the HubIds service so that we're
        # guaranteed to get exactly the events *that* service receives.
        events = getService(wrapped_self, EventSubscription)
        events.subscribe(wrapped_self, IObjectAddedEvent)
        wrapped_self.currentlySubscribed = True
    subscribe = ContextMethod(subscribe)

    def unsubscribe(wrapped_self):
        if not wrapped_self.currentlySubscribed:
            raise RuntimeError, "not subscribed; please subscribe first"
        events = getService(wrapped_self, EventSubscription)
        events.unsubscribe(wrapped_self, IObjectAddedEvent)
        wrapped_self.currentlySubscribed = False
    unsubscribe = ContextMethod(unsubscribe)

    def isSubscribed(self):
        return self.currentlySubscribed

    def registerExisting(wrapped_self):
        object = findContentObject(wrapped_self)
        hub = getService(wrapped_self, HubIds)
        wrapped_self._registerTree(object, hub)
    registerExisting = ContextMethod(registerExisting)

    def _registerTree(wrapped_self, object, hub):
        wrapped_self._registerObject(object, hub)
        # XXX Policy decision: only traverse into folders
        if not IFolder.isImplementedBy(object):
            return
        # Register subobjects
        names = object.keys()
        traversable = getAdapter(object, ITraversable)
        for name in names:
            sub_object = traverseName(object, name, traversable=traversable)
            wrapped_self._registerTree(sub_object, hub)
    _registerTree = ContextMethod(_registerTree)

    def _registerObject(wrapped_self, location, hub):
        # XXX Policy decision: register absolutely everything
        try:
            hub.register(location)
        except ObjectHubError:
            # Already registered
            pass
    _registerObject = ContextMethod(_registerObject)

def findContentObject(context):
    # We want to find the (content) Folder in whose service manager we
    # live.  There are man y way to do this.  Perhaps the simplest is
    # looking for '++etc++site' in the location.  We could also
    # walk up the path looking for something that implements IFolder;
    # the service manager and packages don't implement this.  Or
    # (perhaps better, because a service manager might be attached to
    # a non-folder container) assume we're in service space, and walk
    # up until we find a service manager, and then go up one more
    # step.  Walking up the path could be done by stripping components
    # from the end of the path one at a time and doing a lookup each
    # time, or more directly by traversing the context.  Traversing
    # the context can be done by getting the context and following the
    # chain back; there's a convenience class, ContainmentIterator to
    # do that.  Use the version of ContainmentIterator from
    # zope.proxy, which is aware of the complications caused by
    # security proxies.

    # For now, we pick the first approach.
    location = getPath(context)
    
    index = location.find('/++etc++site/')
    if index != -1:
        location = location[:index]
    else:
        raise ValueError, "can't find '++etc++site' in path"
    root = getRoot(context)
    return traverse(root, location)

