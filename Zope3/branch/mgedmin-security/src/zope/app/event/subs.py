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

$Id: subs.py,v 1.28 2004/03/13 23:55:00 srichter Exp $
"""
from zope.exceptions import NotFoundError
from persistent import Persistent
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree

from zope.proxy import removeAllProxies

from zope.app.traversing import getPath
from zope.app.traversing import canonicalPath, traverse
from zope.app.event.interfaces import IEvent, ISubscriber, ISubscribable
from zope.app.event.interfaces import ISubscribingAware

from zope.component import getService, queryService
from zope.app.servicenames import HubIds
from zope.app.interface.type import PersistentTypeRegistry
from cPickle import dumps, PicklingError
from zope.interface import implements
from zope.app.container.contained import Contained

import logging

__metaclass__ = type

class Subscribable(Persistent, Contained):
    """A local mix-in"""

    implements(ISubscribable)

    def __init__(self):
        # the type registry
        #   key is an event interfaces
        #   value is a list of tuples (subscriber_token, filter)
        self._registry = PersistentTypeRegistry()

        # hubId : { event_type : number of subscriptions }
        self._hubIds = IOBTree()
        # path : { event_type : number of subscriptions }
        self._paths = OOBTree()

    def subscribe(wrapped_self, reference, event_type=IEvent, filter=None):
        '''See ISubscribable'''
        if filter is not None:
            try:
                dumps(filter)
            except PicklingError:
                raise ValueError('The filter argument must be picklable',
                                 filter)

        if not event_type.extends(IEvent, strict=False):
            raise TypeError('event_type must be IEvent or extend IEvent',
                            event_type)
        reftype, token, wrapped_object, clean_object = getWayToSubscribe(
                wrapped_self, reference)

        # If wrapped_object is None, the object can't be traversed to,
        # so raise an exception
        if wrapped_object is None:
            raise NotFoundError(reference)

        clean_self = removeAllProxies(wrapped_self)

        if clean_object is clean_self:
           raise RuntimeError("Cannot subscribe to self")

        # Check that ISubscriber adapter exists for the wrapped object.
        # This will raise an error if there is no such adapter.
        ISubscriber(wrapped_object)

        # Optimisation
        if event_type is IEvent:
            ev_type = None
        else:
            ev_type = event_type

        subscribers = clean_self._registry.get(ev_type)
        if subscribers is None:
            subscribers = []
        subscribers.append((token, filter))
        # Ensure that type registry is triggered for persistence
        clean_self._registry.register(ev_type, subscribers)

        # increment the subscription count for this subscriber
        if reftype is int:
            tokens = clean_self._hubIds
        elif reftype is unicode:
            tokens = clean_self._paths
        else:
            raise AssertionError('reftype must be int or unicode')

        # evtype_numsubs is a dict {ev_type : number of subscriptions}
        evtype_numsubs = tokens.get(token, {})
        evtype_numsubs.setdefault(ev_type, 0)
        evtype_numsubs[ev_type] += 1
        tokens[token] = evtype_numsubs

        subscribingaware = ISubscribingAware(wrapped_object, None)
        if subscribingaware is not None:
            subscribingaware.subscribedTo(wrapped_self, event_type, filter)

        return token

    def unsubscribe(wrapped_self, reference, event_type, filter=None):
        'See ISubscribable. Remove just one subscription.'
        # Remove just one subscription.
        # If reference is an int, try removing by hubId, and if that fails
        # try by path.
        # If reference is a string, try removing by path, and if that fails
        # try by hubId.
        # If reference is an object, try removing by hubId and if that fails,
        # try by path.

        # check that filter is picklable
        if filter is not None:
            try:
                dumps(filter)
            except PicklingError:
                raise ValueError('The filter argument must be picklable',
                                 filter)
        # check that event_type is an IEvent
        if not event_type.extends(IEvent, strict=False):
            raise TypeError('event_type must extend IEvent', event_type)

        # Optimisation
        if event_type is IEvent:
            ev_type = None
        else:
            ev_type = event_type

        clean_self = removeAllProxies(wrapped_self)
        cleanobj, wrappedobj, path, hubId, reftype = getWaysToSubscribe(
            wrapped_self, reference)

        if path is None and hubId is None:
            raise ValueError('Can get neither path nor hubId for reference',
                             reference)

        if cleanobj is None:
            logging.getLogger('SiteError').warn(
                "Unsubscribing an object that doesn't exist: %s" % reference)

        registry = clean_self._registry

        if reftype is unicode:
            where_to_search = ((path, clean_self._paths),
                               (hubId, clean_self._hubIds))
        else:
            where_to_search = ((hubId, clean_self._hubIds),
                               (path, clean_self._paths))

        for token, tokens in where_to_search:

            if token is not None:
                evtype_numsubs = tokens.get(token)
                if evtype_numsubs is not None:
                    numsubs = evtype_numsubs.get(ev_type)
                    if numsubs:

                        # Go through the registrations in self._registry for
                        # exactly ev_type, looking for the first occurence
                        # of (path, filter)
                        subscriptions = registry.get(ev_type)
                        try:
                            subscriptions.remove((token, filter))
                        except ValueError:
                            # The subscription (token, filter) was not present
                            pass
                        else:
                            if subscriptions:
                                registry.register(ev_type, subscriptions)
                            else:
                                registry.unregister(ev_type)

                            if numsubs == 1:
                                del evtype_numsubs[ev_type]
                            else:
                                evtype_numsubs[ev_type] = numsubs - 1
                            if evtype_numsubs:
                                tokens[token] = evtype_numsubs
                            else:
                                del tokens[token]

                            break
        else:
            # No subscription was removed.
            raise NotFoundError(reference)

        subscribingaware = ISubscribingAware(wrappedobj, None)
        if subscribingaware is not None:
            subscribingaware.unsubscribedFrom(wrapped_self, event_type, filter)

    def unsubscribeAll(wrapped_self, reference, event_type=IEvent):
        'See ISubscribable. Remove all matching subscriptions.'
        # check that event_type is an IEvent
        if not IEvent.isEqualOrExtendedBy(event_type):
            raise TypeError('event_type must extend IEvent')

        clean_self = removeAllProxies(wrapped_self)
        cleanobj, wrappedobj, path, hubId, reftype = getWaysToSubscribe(
            wrapped_self, reference)

        if path is None and hubId is None:
            raise ValueError('Can get neither path nor hubId for reference',
                             reference)

        if cleanobj is None:
            logging.getLogger('SiteError').warn(
                "Unsubscribing all for an object that doesn't exist: %s" %
                reference)

        subscribingaware = ISubscribingAware(wrappedobj, None)

        registry = clean_self._registry
        if event_type is IEvent:
            ev_type = None
        else:
            ev_type = IEvent
        eventtypes = registry.getTypesMatching(ev_type)

        eventtypes_used = {}  # used as a set, so values are all None
        num_registrations_removed = 0
        num_subscriptions_removed = 0
        for token, tokens in ((path, clean_self._paths),
                              (hubId, clean_self._hubIds)):

            if token is not None:
                evtype_numsubs = tokens.get(token)
                if evtype_numsubs is not None:
                    for et in eventtypes:
                        numsubs = evtype_numsubs.get(et)
                        if numsubs is not None:
                            num_subscriptions_removed += numsubs
                            del evtype_numsubs[et]
                            eventtypes_used[et] = None  # add key to the set
                    if not evtype_numsubs:
                        del tokens[token]

        for et in eventtypes_used:
            subscriptions = []
            for token, filter in registry.get(et):
                if token == path or token == hubId:
                    num_registrations_removed += 1
                    if subscribingaware is not None:
                        subscribingaware.unsubscribedFrom(
                            wrapped_self, et or IEvent, filter)
                else:
                    subscriptions.append((token, filter))
            if subscriptions:
                registry.register(et, subscriptions)
            else:
                registry.unregister(et)

        assert num_registrations_removed == num_subscriptions_removed
        return num_registrations_removed

    def resubscribeByHubId(wrapped_self, reference):
        'Where a subscriber has a hubId, resubscribe it by that hubid'
        clean_self = removeAllProxies(wrapped_self)
        cleanobj, wrappedobj, path, hubId, reftype = getWaysToSubscribe(
            wrapped_self, reference)

        if hubId is None:
            raise ValueError('Cannot get hubId for reference', reference)

        if path is None:
            raise ValueError('Cannot get path for reference', reference)

        if cleanobj is None:
            # Perhaps this should raise an exception?
            logging.getLogger('SiteError').warn(
                "resubscribeByHubId for an object that doesn't exist: %s" %
                reference)

        self._resubscribe(path, clean_self._paths, hubId, clean_self._hubIds)
        
    def resubscribeByPath(wrapped_self, reference):
        clean_self = removeAllProxies(wrapped_self)
        cleanobj, wrappedobj, path, hubId, reftype = getWaysToSubscribe(
            wrapped_self, reference)

        if path is None:
            raise ValueError('Cannot get path for reference', reference)

        if hubId is None:
            raise ValueError('Cannot get hubId for reference', reference)

        if cleanobj is None:
            # Perhaps this should raise an exception?
            logging.getLogger('SiteError').warn(
                "resubscribeByPath for an object that doesn't exist: %s" %
                reference)

        self._resubscribe(hubId, clean_self._hubIds, path, clean_self._paths)

    def iterSubscriptions(wrapped_self, reference=None, event_type=IEvent):
        '''See ISubscribable'''
        if reference is None:
            return wrapped_self._iterAllSubscriptions(wrapped_self, event_type)
        else:
            return wrapped_self._iterSomeSubscriptions(wrapped_self,
                                                       reference,
                                                       event_type)

    def _iterAllSubscriptions(self, wrapped_self, event_type):
        clean_self = removeAllProxies(wrapped_self)
        if event_type is IEvent:
            ev_type = None
        else:
            ev_type = event_type
        registry = clean_self._registry
        eventtypes = registry.getTypesMatching(ev_type)
        for et in eventtypes:
            subscribers = registry.get(et)
            if et is None:
                et = IEvent
            for token, filter in subscribers:
                yield token, et, filter

    def _iterSomeSubscriptions(self, wrapped_self, reference, event_type):
        clean_self = removeAllProxies(wrapped_self)

        cleanobj, wrappedobj, path, hubId, reftype = getWaysToSubscribe(
            wrapped_self, reference)

        if path is None and hubId is None:
            raise ValueError('Can get neither path nor hubId for reference',
                             reference)

        if cleanobj is None:
            logging.getLogger('SiteError').warn(
                "iterSubscriptions for an object that doesn't exist: %s" %
                reference)
        if event_type is IEvent:
            ev_type = None
        else:
            ev_type = event_type
        registry = clean_self._registry
        eventtypes = registry.getTypesMatching(ev_type)
        eventtypes_used = {}  # used as a set, so values are all None

        for token, tokens in ((path, clean_self._paths),
                              (hubId, clean_self._hubIds)):

            if token is not None:
                evtype_numsubs = tokens.get(token)
                if evtype_numsubs is not None:
                    for et in eventtypes:
                        numsubs = evtype_numsubs.get(et)
                        if numsubs is not None:
                            eventtypes_used[et] = None  # add key to the set

        for et in eventtypes_used:
            if et is None:
                et = IEvent
            for token, filter in registry.get(et):
                if token == path or token == hubId:
                    yield token, et, filter

    def _resubscribe(self, fromtoken, fromsubs, totoken, tosubs):
        path_evtype_numsubs = fromsubs.get(fromtoken)
        if not path_evtype_numsubs:
            # nothing to do
            return 0
        del fromsubs[fromtoken]
        hubId_evtype_numsubs = tosubs.get(totoken, {})
        num_registrations_converted = 0
        num_subscriptions_converted = 0
        registry = self._registry
        for ev_type, num_subscriptions in path_evtype_numsubs.iteritems():
            num_subscriptions_converted += num_subscriptions
            hubId_evtype_numsubs[ev_type] = (
                hubId_evtype_numsubs.get(ev_type, 0) + num_subscriptions)

            subscriptions = registry.get(ev_type)
            if subscriptions:
                new_subscriptions = []
                for token, filter in registry.get(ev_type):
                    if token == fromtoken:
                        new_subscriptions.append((totoken, filter))
                        num_registrations_converted += 1
                    else:
                        new_subscriptions.append((token, filter))
                registry[ev_type] = new_subscriptions

            # I'm not using this one-liner because I want to count the number
            # of registrations converted for sanity-checking.
            #
            # registry[ev_type] = [
            #       (token==fromtoken and totoken or token, filter)
            #       for token, filter in registry.get(ev_type)
            #       ]

        if hubId_evtype_numsubs:
            tosubs[totoken] = hubId_evtype_numsubs

        assert num_registrations_converted == num_subscriptions_converted
        return num_subscriptions_converted

num = 0
class SubscriptionTracker:
    "Mix-in for subscribers that want to know to whom they are subscribed"

    implements(ISubscribingAware)

    def __init__(self):
        self._subscriptions = ()
        global num
        self.number = num
        num += 1

    def subscribedTo(self, subscribable, event_type, filter):
        # XXX insert super() call here
        # This raises an error for subscriptions to global event service.
        subscribable_path = getPath(subscribable)
        self._subscriptions += ((subscribable_path, event_type, filter),)

    def unsubscribedFrom(self, subscribable, event_type, filter):
        # XXX insert super() call here
        # This raises an error for subscriptions to global event service.
        subscribable_path = getPath(subscribable)
        sub = list(self._subscriptions)
        sub.remove((subscribable_path, event_type, filter))
        self._subscriptions = tuple(sub)

def getWayToSubscribe(context, reference):
    '''Figure out the most appropriate means of subscribing the subscriber.

    Returns a tuple:
        (subscription_token, token-type, wrapped_subscriber_object)
    '''
    clean, wrapped, path, hubId, reftype = getWaysToSubscribe(
        context, reference, allways=False)
    if reftype is unicode or hubId is None:
        return unicode, path, wrapped, clean
    if path is None and hubId is None:
        raise Exception('Can get neither path nor hubId for reference',
                        reference)
    return int, hubId, wrapped, clean

def getWaysToSubscribe(context, reference, allways=True):
    '''Get the various means of subscription available for the given
    reference.

    Returns a tuple of:
      clean_object, wrapped_object, unicode path, hubId, reftype

    reftype is object, int or unicode.
    '''
    cleanobj = None
    wrappedobj = None
    hubId = None
    path = None

    clean_reference = removeAllProxies(reference)

    if isinstance(clean_reference, int):
        reftype = int
        hubId = clean_reference
        hub = getService(context, HubIds)
        try:
            wrappedobj = hub.getObject(hubId)
        except NotFoundError:
            wrappedobj = None
        else:
            if allways:
                try:
                    # Hub can't resolve the object, but it might still know
                    # the location the object is supposed to be at.
                    path = hub.getLocation(hubId)
                    # XXX remove this next line when objecthub is refactored
                    path = canonicalPath(path)
                except NotFoundError:
                    path = getPath(wrappedobj)
            cleanobj = removeAllProxies(wrappedobj)
    elif isinstance(clean_reference, basestring):
        reftype = unicode
        path = canonicalPath(clean_reference)
        try:
            wrappedobj = traverse(context, path)
        except NotFoundError:
            wrappedobj = None
        else:
            cleanobj = removeAllProxies(wrappedobj)
            if allways:
                hub = queryService(context, HubIds)
                if hub is not None:
                    try:
                        hubId = hub.getHubId(path)
                    except NotFoundError:
                        pass
    else:
        reftype = object
        wrappedobj = reference
        cleanobj = clean_reference
        path = getPath(wrappedobj)
        hub = queryService(context, HubIds)
        if hub is not None:
            try:
                hubId = hub.getHubId(path)
            except NotFoundError:
                pass

    return cleanobj, wrappedobj, path, hubId, reftype
