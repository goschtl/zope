##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""A stupid registration thingie.

In order to do indexing, objects need to be registered with the object
hub.  A real site should define a policy for when objects are to be
registered.  This particular implementation subscribes to
IObjectAddedEvent events from the event service, and registers
absolutely everything.   It also has a way of registering all
pre-existing objects.

XXX This is really just an example!  There are no unit tests, and it
hardcodes all the policy decisions.  Also, it has some "viewish"
properties.  The traversal code in registerExisting could be useful
for creating a general "Find" facility like the Zope2 Find tab.

$Id: subscribers.py,v 1.6 2002/12/21 15:32:57 poster Exp $
"""
__metaclass__ = type

from Interface import Interface
from Persistence import Persistent

from Zope.Event.ISubscriber import ISubscriber
from Zope.App.Event.IObjectEvent import IObjectAddedEvent
from Zope.App.OFS.Content.Folder.Folder import IFolder
from Zope.ContextWrapper import ContextMethod
from Zope.ComponentArchitecture import getService, queryAdapter

from Zope.App.Traversing import traverse, traverseName, \
     getPhysicalPath, getPhysicalRoot
from Zope.App.OFS.Services.ObjectHub.IObjectHub import ObjectHubError

class ISubscriptionControl(Interface):
    def subscribe():
        """Subscribe to the prevailing object hub service."""

    def unsubscribe():
        """Unsubscribe from the object hub service."""

    def isSubscribed():
        """Return whether we are currently subscribed."""

    def registerExisting():
        """Register all existing objects (for some definition of all)."""

class Registration(Persistent):

    __implements__ = ISubscriptionControl, ISubscriber

    def notify(wrapped_self, event):
        """An event occured. Perhaps register this object with the hub."""
        hub = getService(wrapped_self, "ObjectHub")
        wrapped_self._registerObject(event.object, hub)
    notify = ContextMethod(notify)

    currentlySubscribed = False # Default subscription state

    def subscribe(wrapped_self):
        if wrapped_self.currentlySubscribed:
            raise RuntimeError, "already subscribed; please unsubscribe first"
        channel = wrapped_self._getChannel(None)
        channel.subscribe(wrapped_self, IObjectAddedEvent)
        wrapped_self.currentlySubscribed = True
    subscribe = ContextMethod(subscribe)

    def unsubscribe(wrapped_self):
        if not wrapped_self.currentlySubscribed:
            raise RuntimeError, "not subscribed; please subscribe first"
        channel = wrapped_self._getChannel(None)
        channel.unsubscribe(wrapped_self, IObjectAddedEvent)
        wrapped_self.currentlySubscribed = False
    unsubscribe = ContextMethod(unsubscribe)

    def isSubscribed(self):
        return self.currentlySubscribed

    def registerExisting(wrapped_self):
        object = findContentObject(wrapped_self)
        hub = getService(wrapped_self, "ObjectHub")
        wrapped_self._registerTree(object, hub)
    registerExisting = ContextMethod(registerExisting)

    def _registerTree(wrapped_self, object, hub):
        wrapped_self._registerObject(object, hub)
        # XXX Policy decision: only traverse into folders
        if not IFolder.isImplementedBy(object):
            return
        # Register subobjects
        names = object.keys()
        for name in names:
            # XXX Once traverseName is refactored, should get an
            #     ITraversable from object and pass it to traverseName
            sub_object = traverseName(object, name)
            wrapped_self._registerTree(sub_object, hub)
    _registerTree = ContextMethod(_registerTree)

    def _registerObject(wrapped_self, object, hub):
        # XXX Policy decision: register absolutely everything
        try:
            hub.register(object)
        except ObjectHubError:
            # Already registered
            pass
    _registerObject = ContextMethod(_registerObject)

    def _getChannel(wrapped_self, channel):
        if channel is None:
            channel = getService(wrapped_self, "ObjectHub")
        return channel
    _getChannel = ContextMethod(_getChannel)

def findContentObject(context):
    # We want to find the (content) Folder in whose service manager we
    # live.  There are man y way to do this.  Perhaps the simplest is
    # looking for '++etc++Services' in the location.  We could also
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
    # Zope.Proxy, which is aware of the complications caused by
    # security proxies.

    # For now, we pick the first approach.
    location = getPhysicalPath(context)
    # Location is a tuple of strings, starting with '' (for the root)
    for i in range(len(location)):
        if location[i] == "++etc++Services":
            location = location[:i]
            break
    else:
        raise ValueError, "can't find '++etc++Services' in path"
    root = getPhysicalRoot(context)
    return traverse(root, location)
