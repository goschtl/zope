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

from zope.interface import implements

from zope.security.checker import defineChecker, NoProxy
from zope.security.proxy import removeSecurityProxy

from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound

from zope.app import zapi
from zope.app.keyreference.interfaces import IKeyReference
from zope.app.publisher.browser import BrowserView


from zorg.ajax.page import ComposedAjaxPage

from zorg.live.page.interfaces import ILivePage
from zorg.live.page.interfaces import ILivePageManager
from zorg.live.page.event import dict2event
from zorg.live.page.client import LivePageClient


class LivePage(ComposedAjaxPage) :
    """ A Zope3 substitute for the newov.livepage.LivePage    
    
    The initial call of a LivePage (without parameters) returns a page
    that immediately connects a client to the server. After that the client
    asks again and again for new available output. The output consists of 
    JavaScript snippets that are evaluated by the browser.
    
    >>> from zope.publisher.browser import TestRequest
    >>> page = LivePage(None, TestRequest())
    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(ILivePage, page)
    True
 
    """
        
    implements(ILivePage)
    
    clientFactory = LivePageClient
        
    def notify(self, event) :
        """ Default implementation of an event handler. Must be specialized. """
        pass
        
    notify = classmethod(notify)
        
                   
    def nextClientId(self) :
        """ Returns a new client id. """

        return self.clientFactory(self).uuid
        
    def getLocationId(self) :
        """ Returns a group id that allows to share different livepages
            in different contexts.
            
            The default implementation returns the IKeyReference of the
            LivePage context.
        """
        key = IKeyReference(self.context, None)
        if key :
            return key.__hash__()
        return 0
        
            
    def output(self, uuid) :
        """ Convenience function that accesses a specific client.
        
        """
        request = self.request
        method = Output(self, request).publishTraverse(request, uuid)
        return str(method())

    def input(self, uuid, event=None) :
        """ Convenience function that accesses a specific client.
        
        """
        request = self.request
        if event is None :
            event = dict2event(request.form)
        method = Input(self, request).publishTraverse(request, uuid)
        return method(event)
 
    def sendEvent(cls, event) :
        """ Sends a livepage response to all clients. 
         
        """
        manager = zapi.getUtility(ILivePageManager)
        manager.addEvent(event)
        return ''
    
    sendEvent = classmethod(sendEvent)
            
    def render(self) :
        """ Renders the client and returns the HTML for the browser. """
        NotImplemented

defineChecker(LivePage, NoProxy)
  

class ClientIO(BrowserView) :
    """ A view that represents the input and 
        output of a single client. """  

    def __init__(self, context, request) :
        super(BrowserView, self).__init__(context, request)
        self.view = removeSecurityProxy(context)

    def traverseClient(self, request, uuid) :
        manager = zapi.getUtility(ILivePageManager)
        client = manager.get(uuid)
        if client is None :
            client = self.view.clientFactory(self.view, uuid)
        return client       
            
class Output(ClientIO) :
    """ A view of a LivePage view that allows to traverse to a specific
        client.
        
    """
    
    implements(IPublishTraverse)
      
    def publishTraverse(self, request, uuid) :

        client = self.traverseClient(request, uuid)
        return client.output
       
       
class Input(ClientIO) :
    """ A view of a LivePage view that allows to traverse to a specific
        client.
        
    """
    
    implements(IPublishTraverse)
      
    def publishTraverse(self, request, uuid) :
        client = self.traverseClient(request, uuid)
        return client.input

