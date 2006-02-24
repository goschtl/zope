##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: manager.py 39651 2005-10-26 18:36:17Z oestermeier $
"""
import zope, time

import zope.event
from zope.interface import implements
from zope.app import zapi

from zorg.edition.interfaces import IUUIDGenerator

from zorg.live.page.interfaces import ILivePageManager
from zorg.live.page.cache import Cache

from zorg.live.page.event import ReloadEvent
from zorg.live.page.event import ErrorEvent
from zorg.live.page.event import LoginEvent
from zorg.live.page.event import LogoutEvent


class LivePageManager(object) :
    """ Groups collections of LivePages relative to locations specified
        by ids.
    
        Holds a dict of dict of LivePageClients with location ids and
        client uuids as keys and clients as values.
        
        Makes all write operations thread safe.
        
        See live/README.txt for usage.
        
        
        >>> from zope.interface.verify import verifyObject
        >>> verifyObject(ILivePageManager, LivePageManager())
        True
         
    """
    
    implements(ILivePageManager)
    
    checkInterval = 10              # check for dead clients in seconds
    maxClients = 10                 # max clients per user
    cacheSize = 20                  # cache sizes
    
    def __init__(self) :
        self.locations = Cache(max_size=self.cacheSize)
        self.lastCheck = 0
        self.results = Cache(max_size=self.cacheSize)
                      
    def cacheResult(self, result) :
        """ Caches a result for efficient access. 
        
        Returns a UUID which can be used to retrive the result.
        
        >>> manager = LivePageManager()
        >>> uuid = manager.cacheResult(42)
        >>> manager.fetchResult(uuid)
        42
            
        """
        
        uuid = zapi.getUtility(IUUIDGenerator)()
        self.results[uuid] = result
        return uuid
        
    def fetchResult(self, uuid, clear=True) :
        """ Accesses the result and clears the memory

        >>> manager = LivePageManager()
        >>> uuid = manager.cacheResult(42)
        >>> manager.fetchResult(uuid)
        42

        """
        result = self.results.get(uuid, None)
        if clear :
            del self.results[uuid]
            
        return result
        
    def _location(self, where) :
        """ Internal method that returns a dict of uuid, client tuples
            that belong to a location specified by a location id.
            
        >>> manager = LivePageManager()
        >>> manager._location(42)
        {}
        
        """
        
        return self.locations.setdefault(where, Cache(max_size=self.cacheSize))
        
    def register(self, client, uuid=None) :
        """ Register a client. Uses the provided uuid or generates a new one.
      
        """
        
        existing = None
        
        if uuid is None :
            uuid = zapi.getUtility(IUUIDGenerator)()
        else :
            # an existing uuid indicates a renewed registration of an
            # old page. We do not know what happened so a reload
            # would make sense
            client.addEvent(ReloadEvent())
         
        existing = self.getClientsFor(client.principal.id)
        
        if len(existing) > self.maxClients :
            for c in existing :
                self.unregister(c)
            client.addEvent(ErrorEvent(description="clients exceeded"))
            
        where = client.where
        
        client.uuid = uuid
        if uuid in self._location(where) :
            print "***WARNING: already registered"
        else :
            self._location(where)[uuid] = client
            
        if not existing :
            login = LoginEvent(who=client.principal.id, where=where)
            # we use the zope event here since it's up the concrete
            # pages how they represent the online status of members
            
            zope.event.notify(login)
              

     
    def unregister(self, client) :
    
        where = client.where
        try :
            del self._location(where)[client.uuid]
            print "***Info: unregistered client for %s." % client.principal.title
        except KeyError :
            print "***Info: client already unregistered."
            
        if not self.isOnline(client.principal.id) :
            logout = LogoutEvent(who=client.principal.id, where=where)
            # we use the zope event here since it's up the concrete
            # pages how they represent the online status of members
            zope.event.notify(logout)    
    
    def getClientsFor(self, user_id, where=None) :
        """ Get clients for a specific user.
        """
        return [c for c in self._iterClients(where) if c.principal.id == user_id]
 
    def get(self, uuid, default=None) :
        self.checkAlive()
        for mapping in self.locations.values() :
            if uuid in mapping :
                client = mapping[uuid]
                client.touched = time.time()
                return client
        return default
        
    def checkAlive(self, verbose=False) :
        """ Checks whether clients are alive. """
        if time.time() < self.lastCheck + self.checkInterval :
            return
            
        if verbose :
            for mapping in self.locations.values() :
                for client in mapping.values() :
                    print "Client", client.principal.id
                    
        for mapping in self.locations.values() :
            for client in mapping.values() :
                if time.time() > client.touched + client.targetTimeout :
                    self.unregister(client)
        
        self.lastCheck = time.time()
        
    def _iterClients(self, where=None) :
        """ 
        
        
        """
        if where is None :
            for mapping in self.locations.values() :
                for client in mapping.values() :
                    yield client
        else :
            for client in self._location(where).values() :
                yield client
        
        
    def __iter__(self) :
        """ Iterates over all clients which are still alive.
            Unregisters all unnecessary clients.
        """
        self.checkAlive()
        return self._iterClients()  
        
                
    def addEvent(self, event) :
        self.checkAlive()
        recipients = event.recipients
        where = event.where
        for client in self._iterClients(where) :
            if recipients == "all" or client.principal.id in recipients :
                client.addEvent(event)    

    def whoIsOnline(self, where) :
        """ Returns the ids of the principals that are using livepages. """
        self.checkAlive()
        online = set()
        for client in self._iterClients(where) :
            online.add(client.principal.id)
        return sorted(online)
        
    def isOnline(self, principal_id) :
        """ Returns True iff the user is already online. """
        
        for client in self._iterClients() :
            if client.principal.id == principal_id :
                return True
        return False
            
livePageManager = LivePageManager()            

def livePageSubscriber(event) :
    """ A subscriber that allows the clients to respond to
        Zope3 events.
        
        It checkes whether the clients are still alive (via
        the __iter__ method of the clients).
        
        The events are send to the notify **classmethod**
        of the page classes.
        
    """
        
    manager = zapi.queryUtility(ILivePageManager)
    if manager is None :
        return
        
    page_classes = set()
    for client in manager :
        page_classes.add(client.page_class)
      
    for cls in page_classes :
        cls.notify(event)

