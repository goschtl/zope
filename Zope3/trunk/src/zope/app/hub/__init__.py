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

$Id: __init__.py,v 1.4 2004/03/13 23:55:01 srichter Exp $
"""
__metaclass__ = type

import random

from zope.app import zapi
from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree

from zope.component import getService
from zope.exceptions import NotFoundError
from zope.proxy import removeAllProxies
from zope.app.servicenames import EventSubscription

from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.container.interfaces import IObjectMovedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.event.interfaces import IObjectEvent
from zope.app.event.interfaces import ISubscriber
from zope.app.event.interfaces import IObjectCreatedEvent
from zope.app.event.interfaces import IObjectModifiedEvent
from zope.app.hub.interfaces import IObjectHub, ObjectHubError
from zope.app.hub.interfaces import IObjectRegisteredHubEvent
from zope.app.hub.interfaces import IObjectUnregisteredHubEvent
from zope.app.hub.interfaces import IObjectModifiedHubEvent
from zope.app.hub.interfaces import IObjectMovedHubEvent
from zope.app.hub.interfaces import IObjectRemovedHubEvent
from zope.app.hub.interfaces import ISubscriptionControl
from zope.app.site.interfaces import ISimpleService
from zope.app.traversing.interfaces import ITraverser, ITraversable
from zope.app.folder.interfaces import IFolder
from zope.app.container.contained import ObjectAddedEvent
from zope.interface import implements
from zope.app.event.localservice import ServiceSubscriberEventChannel
from zope.app.servicenames import HubIds

from zope.app.traversing \
     import getPath, canonicalPath, traverse, traverseName, getRoot
from persistent import Persistent
from zope.app.container.contained import Contained

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
            adapter = ITraverser(self.hub)
            try:
                obj = self.__object = adapter.traverse(self.location)
            except NotFoundError:
                pass
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

def canonicalSlash(parent, name=None):
    # Return a canonical path, with a slash appended
    path = canonicalPath(parent)
    if not path.endswith(u'/'):
        path += u'/'
    if name:
        path += name + u'/'
    return path

def userPath(path):
    # Return a path for presentation to a user/external agent -- trailing 
    # slash is omitted
    if path.endswith(u'/') and len(path) > 1:
        return path[:-1]
    else:
        return path

class ObjectHub(ServiceSubscriberEventChannel, Contained):

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

    def notify(self, event):
        '''See interface ISubscriber'''
        self._notify(self, event)

        # XXX all of these "if"s are BS.  We should subscribe to the
        # different kinds of events independently.
        # XXX not sure about this being BS -- we'd still have to explicitly
        # check whether an IObjectMovedEvent event is a 'moved', 'added', or
        # 'removed'.
        
        if IObjectMovedEvent.providedBy(event) and \
            not IObjectAddedEvent.providedBy(event):
            pathslash = canonicalSlash(event.oldParent, event.oldName)
            hubid = self.__path_to_hubid.get(pathslash)      
            if hubid is not None:
                if IObjectRemovedEvent.providedBy(event):
                    # Removed - update data and publish remove hub event
                    self._removeDescendants(pathslash)
                    event = ObjectRemovedHubEvent(
                        event.object, hubid, userPath(pathslash), 
                        event.object)
                    self._notify(self, event)
                else:
                    # Moved - update data and publish moved hub event
                    new_pathslash = canonicalSlash(
                        event.newParent, event.newName)
                    self._repathDescendants(pathslash, new_pathslash)
                    event = ObjectMovedHubEvent(
                        self, hubid, userPath(pathslash),
                        userPath(new_pathslash), event.object)
                    self._notify(self, event)

        elif IObjectModifiedEvent.providedBy(event):
            # Modified - publish modified hub event
            pathslash = canonicalSlash(zapi.getPath(event.object))
            hubid = self.__path_to_hubid.get(pathslash)
            if hubid is not None:
                event = ObjectModifiedHubEvent(
                    self, hubid, userPath(pathslash), event.object)
                self._notify(self, event)

    def _repathDescendants(self, curParent, newParent):
        """Updates the paths of all objects that have curParent as their
        ancestor. curParent is the path of the current common ancestor and
        newParent is the path of the new common ancestor. For example, if
        the following objects are registered:

            1: /foo/
            2: /foo/bar/
            3: /baz/

        _repathDescendants('/foo/', '/foo2/') will modify the registrations
        as follows:

            1: /foo2/
            2: /foo2/bar/
            3: /baz/
        """
        path_to_hubid = self.__path_to_hubid
        hubid_to_path = self.__hubid_to_path
        curParentLen = len(curParent)
        # use temp storage to avoid modifying path_to_hubid during iteration
        toRepath = []
        for path in path_to_hubid.keys():
            if path.startswith(curParent):
                toRepath.append(path)
        for path in toRepath:
            hubid = path_to_hubid[path]
            newPath = newParent + path[curParentLen:]
            if path_to_hubid.has_key(newPath):
                raise ObjectHubError(
                    'Cannot move path %s to %s - target path exists'
                    % (path, newPath))
            del path_to_hubid[path]
            path_to_hubid[newPath] = hubid
            hubid_to_path[hubid] = newPath

    def _removeDescendants(self, curParent):
        """Removes the registration data for all objects that have curParent
        as their ancestor. For example, if the following objects are
        registered:

            1: /foo/
            2: /foo/bar/
            3: /baz/

        _removeDescendants('/foo/') will modify the registrations as follows:

            3: /baz/
        """
        path_to_hubid = self.__path_to_hubid
        hubid_to_path = self.__hubid_to_path
        curParentLen = len(curParent)
        # use temp storage to avoid modifying path_to_hubid during iteration
        toRemove = []
        for path in path_to_hubid.keys():
            if path.startswith(curParent):
                toRemove.append(path)
        for path in toRemove:
            hubid = path_to_hubid[path]
            del hubid_to_path[hubid]
            del path_to_hubid[path]

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
            return userPath(self.__hubid_to_path[hubid])
        except KeyError:
            raise NotFoundError(hubid)

    def getObject(self, hubid):
        '''See interface IObjectHub'''
        path = self.getPath(hubid)
        adapter = ITraverser(self)
        return adapter.traverse(path)

    def register(self, path_or_object):
        '''See interface ILocalObjectHub'''

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

        path_to_hubid = self.__path_to_hubid
        if path_to_hubid.has_key(pathslash):
            raise ObjectHubError('path %s already in object hub' % path)
        hubid = self._generateHubId(pathslash)
        path_to_hubid[pathslash] = hubid

        # send out IObjectRegisteredHubEvent to plugins
        event = ObjectRegisteredHubEvent(
            self, hubid, userPath(pathslash), obj)
        self._notify(self, event)
        return hubid

    def unregister(self, path_or_object_or_hubid):
        '''See interface ILocalObjectHub'''
        if isinstance(path_or_object_or_hubid, (unicode, str)):
            path = canonicalPath(path_or_object_or_hubid)
        elif isinstance(path_or_object_or_hubid, int):
            path = self.getPath(path_or_object_or_hubid)
        else:
            path = getPath(path_or_object_or_hubid)

        pathslash = canonicalSlash(path)

        path_to_hubid = self.__path_to_hubid
        hubid_to_path = self.__hubid_to_path
        try:
            hubid = path_to_hubid[pathslash]
        except KeyError:
            raise NotFoundError('path %s is not in object hub' % path)
        else:
            del hubid_to_path[hubid]
            del path_to_hubid[pathslash]

            # send out IObjectUnregisteredHubEvent to plugins
            event = ObjectUnregisteredHubEvent(
                self, hubid, userPath(pathslash))
            self._notify(self, event)

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
        if pathslash == u'/':
            # Optimisation when we're asked for all the registered objects.
            # Returns an IOBTreeItems object.
            for pathslash, hubId in self.__path_to_hubid.iteritems():
                yield userPath(pathslash), hubId

        else:
            # For a search /foo/bar, constrain the paths returned to those
            # between /foo/bar/ and /foo/bar0, excluding /foo/bar0.
            # chr(ord('/')+1) == '0'
            for pathslash, hubId in self.__path_to_hubid.iteritems(
                min=pathslash, max=userPath(pathslash)+u'0', excludemax=True):
                yield userPath(pathslash), hubId

    def iterObjectRegistrations(self, path=u'/'):
        """See interface IHubEventChannel"""
        traverser = ITraverser(self)
        for path, hubId in self.iterRegistrations(path):
            yield (path, hubId, self._safeTraverse(path, traverser))

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


    def _safeTraverse(self, path, traverser):
        try:
            return traverser.traverse(path)
        except NotFoundError:
            return None


    def unregisterMissingObjects(self):
        """Unregisters all missing objects from the hub.

        Returns the number of objects unregistered.

        An object is missing if it is registered with the hub but cannot
        be accessed via traversal.
        """
        missing = []
        for path, hubid, object in self.iterObjectRegistrations():
            if object is None:
                missing.append(path)
        for path in missing:
            self.unregister(path)
        return len(missing)


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


class Registration(Persistent, Contained):

    implements(ISubscriptionControl, ISubscriber)

    def notify(self, event):
        """An event occured. Perhaps register this object with the hub."""

        # XXX quick hack to make sure we *only* register on add events
        # and not on extending events like move events.
        # We still need to sort out move semantics. We certainly don't
        # have it correct now.

        if event.__class__ is ObjectAddedEvent:
            hub = getService(self, HubIds)
            self._registerObject(event.object, hub)

    currentlySubscribed = False # Default subscription state

    def subscribe(self):
        if self.currentlySubscribed:
            raise RuntimeError, "already subscribed; please unsubscribe first"
        # we subscribe to the HubIds service so that we're
        # guaranteed to get exactly the events *that* service receives.
        events = getService(self, EventSubscription)
        events.subscribe(self, IObjectAddedEvent)
        self.currentlySubscribed = True

    def unsubscribe(self):
        if not self.currentlySubscribed:
            raise RuntimeError, "not subscribed; please subscribe first"
        events = getService(self, EventSubscription)
        events.unsubscribe(self, IObjectAddedEvent)
        self.currentlySubscribed = False

    def isSubscribed(self):
        return self.currentlySubscribed

    def registerExisting(self):
        object = findContentObject(self)
        hub = getService(self, HubIds)
        self._registerTree(object, hub)

    def _registerTree(self, object, hub):
        self._registerObject(object, hub)
        # XXX Policy decision: only traverse into folders
        # XXX Ugh! direct dependency on folders
        # Can this be changed to IContentContainer?!?
        if not IFolder.providedBy(object):
            return
        # Register subobjects
        names = object.keys()
        traversable = ITraversable(object)
        for name in names:
            sub_object = traverseName(object, name, traversable=traversable)
            self._registerTree(sub_object, hub)

    def _registerObject(self, location, hub):
        # XXX Policy decision: register absolutely everything
        try:
            hub.register(location)
        except ObjectHubError:
            # Already registered
            pass

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

