from persistent import Persistent
from persistent.dict import PersistentDict
from zope.interface import implements
from zope.app.zapi import getService, getAdapter
from zope.app.services.servicenames import HubIds
from zope.exceptions import NotFoundError
from zope.app.interfaces.event import ISubscriber
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.services.utility import ILocalUtility
from zope.security.proxy import trustedRemoveSecurityProxy

from zope.app.interfaces.container import IRemoveNotifiable, IAddNotifiable
from zope.app.interfaces.container import IContainer
from zope.index.interfaces import ISimpleQuery

from zope.app.container.sample import SampleContainer

# gods save us from 5-deep nested pkgs
import zope.app.interfaces.services.hub as IHub
import zope.app.services.hub as Hub

from zope.app.interfaces.catalog.catalog import ICatalog

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


class CatalogBase(Persistent, SampleContainer):

    implements(ICatalog, ISubscriber, IRemoveNotifiable, 
               IAddNotifiable, IContainer, IAttributeAnnotatable)

    _subscribed = False

    def _newContainerData(self):
        return PersistentDict()

    def getSubscribed(self): 
        return self._subscribed

    def addNotify(self, event):
        self.subscribeEvents(update=False)

    def removeNotify(self, event):
        " be nice, unsub ourselves in this case "
        if self._subscribed:
            self.unsubscribeEvents()

    def clearIndexes(self):
        for index in self.values():
            index.clear()

    def updateIndexes(self):
        eventF = Hub.ObjectRegisteredHubEvent
        objectHub = getService(self, HubIds) 
        allobj = objectHub.iterObjectRegistrations()
        for location, hubid, wrapped_object in allobj:
            evt = eventF(objectHub, hubid, location, wrapped_object)
            for index in self.values():
                index.notify(evt)

    def subscribeEvents(self, update=True):
        if self._subscribed: 
            raise ValueError, "Already subscribed"
        self._subscribed = True
        objectHub = getService(self, HubIds) 
        objectHub.subscribe(self, IHub.IRegistrationHubEvent)
        objectHub.subscribe(self, IHub.IObjectModifiedHubEvent)
        if update:
            self.updateIndexes()

    def unsubscribeEvents(self):
        if not self._subscribed: 
            raise ValueError, "Already unsubscribed"
        self._subscribed = False
        objectHub = getService(self, HubIds) 
        try:
            objectHub.unsubscribe(self, IHub.IRegistrationHubEvent)
            objectHub.unsubscribe(self, IHub.IObjectModifiedHubEvent)
        except NotFoundError:
            # we're not subscribed. bah.
            pass

    def notify(self, event):
        "objecthub is my friend!"

        indexes = self.values()
        for index in indexes:
            try:
                index.notify(event)
            except: # XXX bare excepts are not my friend! Please fix.
                pass

    def searchResults(self, **searchterms):
        from zodb.btrees.IIBTree import intersection
        pendingResults = None
        for key, value in searchterms.items():
            index = self.get(key)
            if not index: 
                raise ValueError, "no such index %s"%(key)
            index = getAdapter(index, ISimpleQuery)
            results = index.query(value)
            # Hm. As a result of calling getAdapter, I get back
            # security proxy wrapped results from anything that
            # needed to be adapted.
            results = trustedRemoveSecurityProxy(results)
            if pendingResults is None:
                pendingResults = results
            else:
                pendingResults = intersection(pendingResults, results)
            if not pendingResults:
                # nothing left, short-circuit
                break
        # Next we turn the IISet of hubids into a generator of objects
        objectHub = getService(self, HubIds) 
        results = ResultSet(pendingResults, objectHub)
        return results

class CatalogUtility(CatalogBase):
    "A Catalog in service-space"
    # Utilities will default to implementing the most specific 
    # interface. This piece of delightfulness is needed because
    # the interface resolution order machinery implements (no
    # pun intended) the old-style Python resolution order machinery.
    implements(ILocalUtility)

class Catalog(CatalogBase): 
    "A content-space Catalog"
    pass
