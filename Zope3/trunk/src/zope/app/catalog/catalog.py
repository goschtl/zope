from __future__ import generators

from persistence import Persistent
from persistence.dict import PersistentDict
from zope.interface import implements
from zope.context import ContextMethod
from zope.app.zapi import getService
from zope.app.services.servicenames import HubIds
from zope.exceptions import NotFoundError
from zope.app.interfaces.services.registration import IRegisterable
from zope.app.interfaces.event import ISubscriber
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.services.utility import ILocalUtility

from zope.app.interfaces.container import IDeleteNotifiable, IAddNotifiable
from zope.app.interfaces.container import IContainer

from zope.app.container.sample import SampleContainer

# gods save us from 5-deep nested pkgs
import zope.app.interfaces.services.hub as IHub
import zope.app.services.hub as Hub

import time

from zope.app.interfaces.catalog.catalog import ICatalogView, ICatalog

class ResultSet:
    "Lazily accessed set of objects"

    def __init__(self, hubidset, hub):
        self.hubidset = hubidset
        self.hub = hub

    def __len__(self):
        return len(self.hubidset)

    def __iter__(self):
        for hubid in self.hubidset:
            obj = self.hub.getObject(hubid)
            yield obj


class Catalog(Persistent, SampleContainer):

    implements(ICatalog, ISubscriber, IDeleteNotifiable, 
               IAddNotifiable, IContainer, IAttributeAnnotatable)

    _subscribed = False

    def _newContainerData(self):
        return PersistentDict()

    def getSubscribed(self): 
        return self._subscribed

    def afterAddHook(wrapped_self, object, container):
        wrapped_self.subscribeEvents(update=False)
    afterAddHook = ContextMethod(afterAddHook)

    def beforeDeleteHook(wrapped_self, object, container):
        " be nice, unsub ourselves in this case "
        if wrapped_self._subscribed:
            wrapped_self.unsubscribeEvents()
    beforeDeleteHook = ContextMethod(beforeDeleteHook)

    def clearIndexes(self):
        for index in self.values():
	    index.clear()

    def updateIndexes(wrapped_self):
	eventF = Hub.ObjectRegisteredHubEvent
        objectHub = getService(wrapped_self, HubIds) 
	allobj = objectHub.iterObjectRegistrations()
	for location, hubid, wrapped_object in allobj:
	    evt = eventF(objectHub, hubid, location, wrapped_object)
	    for index in wrapped_self.values():
		index.notify(evt)
    updateIndexes = ContextMethod(updateIndexes)

    def subscribeEvents(wrapped_self, update=True):
        if wrapped_self._subscribed: 
            raise ValueError, "Already subscribed"
        wrapped_self._subscribed = True
        objectHub = getService(wrapped_self, HubIds) 
        objectHub.subscribe(wrapped_self, IHub.IRegistrationHubEvent)
        objectHub.subscribe(wrapped_self, IHub.IObjectModifiedHubEvent)
        if update:
            wrapped_self.updateIndexes()

    subscribeEvents = ContextMethod(subscribeEvents)

    def unsubscribeEvents(wrapped_self):
        if not wrapped_self._subscribed: 
            raise ValueError, "Already unsubscribed"
        wrapped_self._subscribed = False
        objectHub = getService(wrapped_self, HubIds) 
        try:
            objectHub.unsubscribe(wrapped_self, IHub.IRegistrationHubEvent)
            objectHub.unsubscribe(wrapped_self, IHub.IObjectModifiedHubEvent)
        except NotFoundError:
            # we're not subscribed. bah.
            pass

    unsubscribeEvents = ContextMethod(unsubscribeEvents)

    def notify(wrapped_self, event):
        "objecthub is my friend!"

        indexes = wrapped_self.values()
        if (IHub.IObjectRegisteredHubEvent.isImplementedBy(event) or
            IHub.IObjectModifiedHubEvent.isImplementedBy(event)):
            addobj = event.object
        elif IHub.IObjectUnregisteredHubEvent.isImplementedBy(event):
            delobj = event.object
        for index in indexes:
            try:
                index.notify(event)
            except:
                pass
    notify = ContextMethod(notify)

    def searchResults(wrapped_self, **searchterms):
        from zodb.btrees.IIBTree import intersection
        pendingResults = None
        for key, value in searchterms.items():
            index = wrapped_self.get(key)
            if not index: 
                raise ValueError, "no such index %s"%(key)
            results = index.search(value)
            if pendingResults is None:
                pendingResults = results
            else:
                pendingResults = intersection(pendingResults, results)
            if not pendingResults:
                # nothing left, short-circuit
                break
        # Next we turn the IISet of hubids into a generator of objects
        objectHub = getService(wrapped_self, HubIds) 
        results = ResultSet(pendingResults, objectHub)
        return results
    searchResults = ContextMethod(searchResults)

class CatalogUtility(Catalog):
    implements (ILocalUtility)
