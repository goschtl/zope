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
import Queue

from zope.interface import implements
from zope.app import zapi

from zorg.live.page.interfaces import ILivePageClient
from zorg.live.page.interfaces import ILivePageManager
from zorg.live.page.interfaces import ICloseEvent

from zorg.live.page.event import IdleEvent
from zorg.live.page.event import request2event

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
        self.outbox = Queue.Queue()
      
        self.principal = page.request.principal
        self.touched = time.time()
        manager.register(self, uuid)


    def nextEvent(self) :
        """ Returns an event for processing in the browser side client.
            Touches the client to indicate that the connection 
            is still alive.
        """
        self.touched = time.time()
        try :
            return self.outbox.get_nowait()
        except Queue.Empty :
            return None
    
        
    def addEvent(self, event) :
        """ Adds an output event for further client side processing to the
            clients event queue.
        """
        self.outbox.put(event)
                  
                  
    def output(self) :
        """ Checks the event queue for waiting events until a timeout occurrs.
            
            Returns an idle event after an timeout.
            
            Note that this is a blocking version that can be used
            by a threading server. A non-blocking LivePageServer
            should use nextEvent for defered checks.
            
        """
        output = self.nextEvent()
        if output :
            return str(output)
                
        end = time.time() + self.refreshInterval
        while time.time() < end :
            output = self.nextEvent()
            if output :
                return str(output)
            time.sleep(0.1)
            
        return str(IdleEvent())
        
    def input(self, event=None) :
        """ Receives a client event and broadcasts the event
            to other clients.
        """
        
        if event is None :
            event = request2event()
            
        manager = zapi.getUtility(ILivePageManager)
        
        if ICloseEvent.providedBy(event) and event.uuid == self.uuid :
            manager.unregister(self)
            return ''
            
        manager.addEvent(event)
        return ''

