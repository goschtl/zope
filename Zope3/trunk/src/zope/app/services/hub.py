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

$Id: hub.py,v 1.7 2003/03/19 18:05:03 stevea Exp $
"""

from __future__ import generators

__metaclass__ = type

import random

from zodb.btrees.IOBTree import IOBTree
from zodb.btrees.OIBTree import OIBTree

#from zope.app.traversing import getPath, canonicalPath
from zope.app.traversing import getPhysicalPathString as getPath
from zope.app.traversing import locationAsUnicode as canonicalPath

from zope.component import getAdapter
from zope.exceptions import NotFoundError
from zope.proxy.context import ContextWrapper, isWrapper, ContextMethod
from zope.proxy.introspection import removeAllProxies

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

    __implements__ = (
        IObjectHub,
        ISimpleService,
        ServiceSubscriberEventChannel.__implements__)

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

        # XXX This check should be done by canonicalPath, but Albert is still
        #     refactoring that. So, I'll do it here for now.
        if not pathslash.startswith(u'/'):
            raise ValueError('Path must be absolute, not relative:', path)

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
