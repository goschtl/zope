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
        
        self.group_id = page.getGroupId()
        self.page_class = page.__class__
        self.outbox = []
        self.principal = page.request.principal
        self.writelock = allocate_lock()
        self.touched = time.time()
        manager.register(self, uuid)
            
    def popOutput(self) :
        """ Returns an output block for processing in the browser side client.
            Touches the client to indicate that the connection is still alive.
        """
        self.writelock.acquire()
        try :
            if self.outbox :
                result = self.outbox.pop()
                if result.endswith("timestamp=")  :
                    result += "%s\n" % time.time()
                #enforce that the URLs with dummy timestamps are really reloaded
                #we add the dummy as late as possible to avoid redundant calls
            else :
                result = None
            self.touched = time.time()      
        finally :
            self.writelock.release()
        return result
    
        
    def addOutput(self, output) :
        """ Adds a output block for further client side processing to the
            clients message queue.
        """

        self.writelock.acquire()
        try:
            if output not in self.outbox :
                self.outbox.append(output)
        finally:
            self.writelock.release()        
 
    def output(self, outputNum=0) :
        end = time.time() + self.refreshInterval
        while time.time() < end :
            output = self.popOutput()
            if output :
                time.sleep(0.5)
                #print "sending", output
                return output
            time.sleep(0.1)
        return "idle"
        
    def input(self, handler_name, arguments) :
        js = getattr(self, handler_name)(arguments)
        manager = zapi.getUtility(ILivePageManager)
        manager.addOutput(js)
        return ''

    def alert(self, arguments) :
        args = arguments.split(",")
        return "javascript alert('%s')" % args[0]
        
    def update(self, arguments) :
        args = arguments.split(",")
        return "javascript update('%s')" % args[0]
        
    def append(self, arguments) :
        args = arguments.split(",")
        return "append %s\n%s" % (args[0], args[1])

        