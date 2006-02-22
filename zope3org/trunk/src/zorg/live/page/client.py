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

import time, zope

from thread import allocate_lock

from zope.interface import implements
from zope.app import zapi

from zorg.live.page.interfaces import ILivePageClient
from zorg.live.page.interfaces import ILivePageManager
from zorg.live.page.interfaces import ICloseEvent

from zorg.live.page.event import IdleEvent

class LivePageClient(object):
    """
    An object which represents the client-side webbrowser of a LivePage.
    
    >>> from zorg.live.page.manager import LivePageManager
    >>> zope.component.provideUtility(LivePageManager(), ILivePageManager)
    >>> manager = LivePageManager()
    
    """

    implements(ILivePageClient)
    
    refreshInterval = 10    # seconds
    targetTimeout = 20
    
    def __init__(self, page, uuid=None) :
        
        manager = zapi.getUtility(ILivePageManager)
        
        self.where = page.getLocationId()
        self.page_class = page.__class__
        self.outbox = []
        self.principal = page.request.principal
        self.writelock = allocate_lock()
        self.touched = time.time()
        manager.register(self, uuid)
            
    def nextEvent(self) :
        """ Returns an event for processing in the browser side client.
            Touches the client to indicate that the connection 
            is still alive.
        """
        self.writelock.acquire()
        try :
            if self.outbox :
                result = self.outbox.pop(0)
            else :
                result = None
            self.touched = time.time()      
        finally :
            self.writelock.release()
        return result
    
        
    def addEvent(self, event) :
        """ Adds an output event for further client side processing to the
            clients event queue.
        """

        self.writelock.acquire()
        try:
            if event not in self.outbox :
                self.outbox.append(event)
        finally:
            self.writelock.release()        
 
    def output(self) :
        """ Checks the event queue for waiting events.
            
            Returns an idle event after an timeout.
            
            Note that this is a blocking version that can be used
            by a threading server. A non-blocking LivePageServer
            should use nextEvent for defered checks.
            
        """
            
        end = time.time() + self.refreshInterval
        while time.time() < end :
            output = self.nextEvent()
            if output :
                return str(output)
            time.sleep(0.2)
            
        return str(IdleEvent())
        
    def input(self, event) :
        """ Receives a client event and broadcasts the event
            to other clients.
        """
        
        manager = zapi.getUtility(ILivePageManager)
        
        if ICloseEvent.providedBy(event) and event.uuid == self.uuid :
            manager.unregister(self)
            return ''
            
        manager.addEvent(event)
        return ''

