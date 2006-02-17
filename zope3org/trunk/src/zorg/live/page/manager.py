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

$Id: page.py 39651 2005-10-26 18:36:17Z oestermeier $
"""
import zope, time

from thread import allocate_lock

from zope.interface import implements
from zope.app import zapi

from zorg.edition.interfaces import IUUIDGenerator

from zorg.live.page.interfaces import ILivePageManager
from zorg.live.page.cache import Cache



class LivePageManager(object) :
    """ Groups collections of LivePages.
    
        Holds a dict of dict of LivePageClients with group_ids and
        client uuids as keys and clients as values.
        
        Makes all write operations thread safe.
        
        See live/README.txt for usage.
        
        
        >>> from zope.interface.verify import verifyObject
        >>> verifyObject(ILivePageManager, LivePageManager())
        True
         
    """
    
    implements(ILivePageManager)
    
    writelock = allocate_lock()     # A writelock for clients
    checkInterval = 10              # check for dead clients in seconds
    maxClients = 3                  # max clients per user
    
    def __init__(self) :
        self.groups = {}
        self.lastCheck = 0
        self.results = Cache(size=200)
        
    def cacheResult(self, result) :
        """ Caches a result for efficient access. 
        
        Returns a UUID which can be used to retrive the result.
        
        >>> manager = LivePageManager()
        >>> uuid = manager.cacheResult(42)
        >>> manager.fetchResult(uuid)
        42
            
        """
        
        uuid = zapi.getUtility(IUUIDGenerator)()
        self.writelock.acquire()
        try :
            self.results[uuid] = result
        finally:
            self.writelock.release()
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
        
    def _group(self, group_id) :
        """ Internal method that returns a dict of uuid, client tuples
            that belong to a group specified by a group id.
            
        >>> manager = LivePageManager()
        >>> manager._group(42)
        {}
        
        """
        
        return self.groups.setdefault(group_id, {})
        
    def register(self, client, uuid=None) :
        """ Register a client. Uses the provided uuid or generates a new one.
      
        """
        
        
        self.writelock.acquire()
        try:
            if uuid is None :
                uuid = zapi.getUtility(IUUIDGenerator)()
            else :
                # an existing uuid indicates a renewed registration of an
                # old page. We do not know what happened so a reload
                # would make sense
                client.addOutput("reload")
             
            existing = self.getClientsFor(client.principal.id)
            if len(existing) > self.maxClients :
                for c in existing :
                    self.unregister(c)
                client.addOutput("limited")
                
            group_id = client.group_id
            client.handleid = uuid
            if uuid in self._group(group_id) :
                print "***WARNING: already registered"
            else :
                self._group(group_id)[uuid] = client
        finally:
            self.writelock.release()
     
    def unregister(self, client) :
        self.writelock.acquire()
        try:
            group_id = client.group_id
            try :
                del self._group(group_id)[client.handleid]
                print "***Info: unregistered client for %s." % client.principal.title
            except KeyError :
                print "***Info: client already unregistered."
        finally:
            self.writelock.release()
    
    def getClientsFor(self, user_id, group_id=None) :
        """ Get clients for a specific user.
        """
        return [c for c in self._iterClients(group_id) if c.principal.id == user_id]
 
    def get(self, uuid, default=None) :
        for mapping in self.groups.values() :
            if uuid in mapping :
                client = mapping[uuid]
                self.writelock.acquire()
                try :
                    client.touched = time.time()
                finally :
                    self.writelock.release()    
                return client
        return default
        
    def checkAlive(self, verbose=False) :
        """ Checks whether clients are alive. """
        if time.time() < self.lastCheck + self.checkInterval :
            return
            
        if verbose :
            for mapping in self.groups.values() :
                for client in mapping.values() :
                    print "Client", client.principal.id
                    
        for mapping in self.groups.values() :
            for client in mapping.values() :
                if time.time() > client.touched + client.targetTimeout :
                    self.unregister(client)
        self.writelock.acquire()
        try :
            self.lastCheck = time.time()
        finally :
            self.writelock.release()    
    
    def _iterClients(self, group_id=None) :
        """ 
        
        
        """
        if group_id is None :
            for mapping in self.groups.values() :
                for client in mapping.values() :
                    yield client
        else :
            for client in self._group(group_id).values() :
                yield client
        
        
    def __iter__(self) :
        """ Iterates over all clients which are still alive.
            Unregisters all unnecessary clients.
        """
        self.checkAlive()
        return self._iterClients()  
        
                
    def addOutput(self, output, group_id=None, recipients="all") :
        self.checkAlive()
        for client in self._iterClients(group_id) :
            if recipients == "all" or client.principal.id in recipients :
                client.addOutput(output)    

    def whoIsOnline(self, group_id) :
        """ Returns the ids of the principals that are using livepages. """
        self.checkAlive()
        online = set()
        for client in self._iterClients(group_id) :
            online.add(client.principal.id)
        return sorted(online)
        

livePageManager = LivePageManager()            

def livePageSubscriber(event) :
    """ A subscriber that allows the clients to respond to
        Zope3 events.
        
        It checkes whether the clients are still alive (via
        the __iter__ method of the clients).
        
        The events are send to the notify **classmethod**
        of the page classes.
        
    """
    
    manager = zapi.getUtility(ILivePageManager)
    
    page_classes = set()
    for client in manager :
        page_classes.add(client.page_class)
      
    for cls in page_classes :
        cls.notify(event)

                     
