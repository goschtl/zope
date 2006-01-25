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

$Id: livepage.py 39651 2005-10-26 18:36:17Z oestermeier $
"""
__docformat__ = 'restructuredtext'

import os, itertools, unittest, time
from string import Template
from thread import allocate_lock

from zope.testing import doctest

from zope.app import zapi
from zope.interface import implements
from zope.component import adapts
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces import IRequest
from zope.app.session.interfaces import ISession
from zope.security.proxy import removeSecurityProxy
from zope.security.checker import defineChecker, NoProxy
from zope.security.checker import ProxyFactory

from zope.app.traversing.interfaces import TraversalError
from zope.app.traversing.interfaces import ITraversable
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.app.publisher.browser import BrowserView
from zope.app.keyreference.interfaces import IKeyReference

from zope.interface import implements
from zope.interface import Interface
from zorg.ajax.page import AjaxPage, ComposedAjaxPage


from zorg.ajax.interfaces import ILiveChanges
from zorg.ajax.interfaces import ILivePage
from zope.publisher.http import DirectResult

from twisted.web2.wsgi import FileWrapper

from interfaces import ILivePageClients
from interfaces import ILivePageClient

from zorg.edition.interfaces import IUUIDGenerator

class LivePageClients(object) :
    """ Groups collections of LivePages.
    
        Holds a dict of dict of LivePageClients with group_ids and
        client uuids as keys and clients as values.
        
        Makes all write operations thread safe.
    """
    
    implements(ILivePageClients)
    
    writelock = allocate_lock()     # A writelock for clients
   
    def __init__(self) :
        self.groups = {}
        
    def _group(self, group_id) :
        return self.groups.setdefault(group_id, {})
        
    def register(self, client, uuid=None) :
        self.writelock.acquire()
        try:
            if uuid is None :
                uuid = zapi.getUtility(IUUIDGenerator)()
            group_id = client.group_id
            client.handleid = uuid
            self._group(group_id)[uuid] = client
        finally:
            self.writelock.release()
     
    def unregister(self, client) :
        self.writelock.acquire()
        try:
            group_id = client.group_id
            del self._group(group_id)[client.handleid]
            print "***Info: unregistered client for %s." % client.principal.title
        finally:
            self.writelock.release()
    
    def get(self, uuid, default=None) :
        for mapping in self.groups.values() :
            if uuid in mapping :
                return mapping[uuid]
        return default
        
    def __iter__(self) :
        """ Iterates over all clients which are still alive.
            Unregisters all unnecessary clients.
        """
        for mapping in self.groups.values() :
            for client in mapping.values() :
                if time.time() > client.touched + client.targetTimeout :
                    self.unregister(client)
                else :
                    yield client
                

    def addOutput(self, output, who="all", group_id=None) :
        if who == "all" :
            if group_id is None :
                selected= self
            else :
                selected = self._group(group_id).values()
            for client in selected :
                client.addOutput(output)
            
    def whoIsOnline(self, group_id) :
        """ Returns the ids of the principals that are using livepages. """
        online = set()
        for client in self._group(group_id).values() :
            online.add(client.principal.id)
        return sorted(online)
        
            

def livePageSubscriber(event) :
    """ A subscriber that allows the clients to respond to
        Zope3 events.
        
        It checkes whether the clients are still alive (via
        the __iter__ method of the clients).
        
        The events are send to the notify **classmethod**
        of the page classes.
        
    """
    global clients
    
    page_classes = set()
    for client in clients :
        page_classes.add(client.page_class)
        
    for cls in page_classes :
        cls.notify(event)

                     
       
# A global dictionary shared between threads
clients = LivePageClients()

class LivePageClient(object):
    """An object which represents the client-side webbrowser of a LivePage.
    """

    implements(ILivePageClients)
    
    refreshInterval = 3
    targetTimeout = 20
    
    def __init__(self, page, uuid=None) :
        global clients
        self.group_id = page.getGroupId()
        self.page_class = page.__class__
        self.outbox = []
        self.principal = page.request.principal
        self.writelock = allocate_lock()
        self.touched = time.time()
        if uuid is None :
            clients.register(self)
            
    def popOutput(self) :
        """ Returns an output block for processing in the browser side client.
            Touches the client to indicate that the connection is still alive.
        """
        self.writelock.acquire()
        try :
            if self.outbox :
                result = self.outbox.pop()
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
                return output
            time.sleep(0.1)
        return "idle"
        
    def input(self, handler_name, arguments) :
        js = getattr(self, handler_name)(arguments)
        global clients
        clients.addOutput(js)
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

        
class LivePage(ComposedAjaxPage) :
    """ A Zope3 substitute for the newov.livepage.LivePage    
    
    The initial call of a LivePage (without parameters) returns a page
    that immediately connects a client to the server. After that the client
    asks again and again for new available output. The output consists of 
    JavaScript snippets that are evaluated by the browser.
    
    Here we simulate the startup of two clients of the same factory type:
    
    >>> factory='zorg.ajax.livepage.LivePage'
    
    Note that the factory must be application specific because
    the access and notification method build their own instances.
    
    >>> class Principal(object) :
    ...     def __init__(self, id, title) :
    ...         self.id = id
    ...         self.title = title
    
    >>> user1 = Principal('zorg.member.uwe', u'Uwe Oestmeier')
    >>> user2 = Principal('zorg.member.dominik', u'Dominik Huber')
    
    >>> request = TestRequest()
    >>> request.setPrincipal(user1)
    >>> page = LivePage(None, request)
    >>> group_id = page.getGroupId()
    >>> print page.render()
    <html>
        <head>
            <script src="http://127.0.0.1/++resource++zorgajax/prototype.js" type="text/javascript"></script>
            <script type="text/javascript">var livePageUUID = 'uuid1';</script>
            <script src="http://127.0.0.1/++resource++zorgajax/livepage.js" type="text/javascript"></script>
        </head>
        <body onload="startClient()">
        <p>Input some text.</p>
        <input onchange="sendLivePage('append', 'target', this.value)" type="text" />
        <p id="target">Text goes here:</p>
        </body>
    </html>

    
    >>> request.setPrincipal(user2)
    >>> page = LivePage(None, request)
    >>> print page.render()
    <html>
        <head>
            <script src="http://127.0.0.1/++resource++zorgajax/prototype.js" type="text/javascript"></script>
            <script type="text/javascript">var livePageUUID = 'uuid2';</script>
            <script src="http://127.0.0.1/++resource++zorgajax/livepage.js" type="text/javascript"></script>
        </head>
        <body onload="startClient()">
        <p>Input some text.</p>
        <input onchange="sendLivePage('append', 'target', this.value)" type="text" />
        <p id="target">Text goes here:</p>
        </body>
    </html>
   
    The global clients dictionary can be asked for all online users:
    
    >>> clients.whoIsOnline(group_id)
    ['zorg.member.dominik', 'zorg.member.uwe']
    
    For test purposes we set the refresh interval (i.e. the interval in which
    output calls are renewed) to 0.1 seconds :
    
    >>> LivePageClient.refreshInterval = 0.1
  
    After that the page can be called by the javascript glue as follows
    
    -  @@livepage.html/@@client/uuid0/output?outputNum=0
    
       Call the output method and ask for special output that is intended
       for the specified client
   
    -  @@livepage.html/@@client/uuid0/input?handler-name=change&arguments=42
        
       Call an input method that produces output for various clients.
      
    After the startup we ask for some output. Since nothing happened, the
    output is 'idle':
    
    >>> page1 = LivePage(None, TestRequest())
    >>> page1.output(uuid='uuid1', outputNum=0)
    'idle'
  
    Now we can send some input :
    
    >>> page2 = LivePage(None, TestRequest())
    >>> page2.input(uuid='uuid1', handler_name='append', arguments="target,42")
    ''
    
    After that the next call of the output returns javascript snippets:
        
    >>> print page1.output(uuid='uuid1', outputNum=1)
    append target
    42


    And this again and again if we provide new input :
    
    >>> page2.input(uuid='uuid1', handler_name='append', arguments="target,43")
    ''
    
    >>> print page1.output(uuid='uuid1', outputNum=2)
    append target
    43
   

    """
        
    implements(ILivePage)
    
    clientFactory = LivePageClient
        
    def notify(self, event) :
        """ Default implementation of an event handler. Must be specialized. """
        pass
        
    notify = classmethod(notify)
        
                   
    def nextClientId(self) :
        """ Returns a new client id. """
        
        return self.clientFactory(self).handleid
        
    def getGroupId(self) :
        """ Returns a group id that allows to share different livepages
            in different contexts.
            
            The default implementation returns the IKeyReference of the
            LivePage context.
        """
        
        return IKeyReference(self.context, None) or 0
        
            
    def output(self, uuid, outputNum) :
        """ Convenience function that accesses a specific client.
        
        """
        request = self.request
        method = Output(self, request).publishTraverse(request, uuid)
        return method(outputNum)

    def input(self, uuid, handler_name, arguments) :
        """ Convenience function that accesses a specific client.
        
        """
        request = self.request
        method = Input(self, request).publishTraverse(request, uuid)
        return method(handler_name, arguments)
 
    def sendResponse(self, response) :
        """ Sends a livepage response to all clients. 
            A response consits of a leading command line 
            and optional html body data.
        """
        global clients
        clients.addOutput(response)
        return ''
    
    sendResponse = classmethod(sendResponse)
            
    def render(self) :
        """ A test method that calls the livepage. 
            
            Must be overwritten. The method must call self.nextClientId to
            ensure that a unique key is generated.
            
        """
        
        url = zapi.absoluteURL(self.context, self.request) 
        url += "/++resource++zorgajax"

        template = Template("""<html>
    <head>
        <script src="$url/prototype.js" type="text/javascript"></script>
        <script type="text/javascript">var livePageUUID = '$id';</script>
        <script src="$url/livepage.js" type="text/javascript"></script>
    </head>
    <body onload="startClient()">
    <p>Input some text.</p>
    <input onchange="sendLivePage('append', 'target', this.value)" type="text" />
    <p id="target">Text goes here:</p>
    </body>
</html>""")      
                                                
        return template.substitute(id=self.nextClientId(), url=url)
 

defineChecker(LivePage, NoProxy)
  

class ClientIO(BrowserView) :
    """ A view that represents the input and 
        output of a single client. """  

    def __init__(self, context, request) :
        super(BrowserView, self).__init__(context, request)
        self.view = removeSecurityProxy(context)

    def traverseClient(self, request, uuid) :
        global clients
        client = clients.get(uuid)
        if client is None :
            client = self.view.clientFactory(self.view, uuid)
            clients.register(client, uuid)    
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



class LiveOutputStream(object) :
    """ The iterable output stream. """

    counter = 0
    limit = 100  
    
    def __init__(self, channel, client) :
        self.channel = channel
        self.client = client
        
    def __iter__(self) :
        if self.client.output :
            result = self.client.output.pop()
            yield result
       
        self.counter += 1
        if self.counter > self.limit :
            raise StopIteration
              

defineChecker(LiveOutputStream, NoProxy)



### Experimental Streaming Stuff. Seems to be unnecessary for live pages ###


class IIterable(Interface) :
    
    def __iter__() :
        """ Defines an iterable. """


class FileBuffer(object):
    """ A buffer for shared read and write operations. """
    closed = False
    count = 0
    
    newline = '\n<p>.</p>'
    end = "</body></html>"
    
    def __init__(self):
        self.buf = ''

    def write(self, str):
        self.buf += str

    def read(self, size):
        
        data = self.buf[:size]
        self.buf = self.buf[len(data):]
        if data :
            return data
        elif self.closed :
            return None
        if self.count > 100 :
            self.close()
            
        self.count += 1
        time.sleep(0.1)
        return self.newline
        
    def __iter__(self) :
        data = self.read(100)
        if data is None :
            raise StopIteration
        return data
            
    def close(self) :
        self.write(self.end)
        self.closed = True
  
    def open(self) :
        self.closed = False
        self.count = 0

        
class IterBuffer(FileBuffer) :

    newline = '\n'
    end = ""
    
class LiveChanges(AjaxPage) :
    """ Base class that implements live changes.
    
        The server provides a shared stream. The clients can
        subscribe to the stream events via an potentially infinite 
        streamEvents request and and fire an event with a writeEvent
        operation.
        
        Let's set up a consumer :
        
        >>> consumer = LiveChanges(None, TestRequest())
        >>> result = consumer.streamEvents()
        >>> stream = result.body
        
        Now we create a writer and fire two events :
        
        >>> writer = LiveChanges(None, TestRequest())
        >>> writer.writeEvent("1")
        >>> writer.writeEvent("2")
        
        The consumer can access them in one call :
        
        >>> print stream.next()
        <html><body><p>1</p>

        
        If all events are consumed we get a dummy :
        
        >>> print stream.next()
        <p>2</p>

        
        >>> writer.writeEvent("3")
        >>> print stream.next()
        <p>3</p>

        
        We can also decide to close the connection :
        
        >>> LiveChanges(None, TestRequest()).closeStream()
        >>> print stream.next()
        </body></html>


    """
    
    implements(ILiveChanges)

            
    buffer = FileBuffer()    # shared file buffer
    
     
    def streamEvents(self) :
        """ Dummy implementation of an unlimited stream of change events.
            
            Should be overwritten by the target class.
 
        """
        
        from zope.publisher.http import IResult
        from zope.publisher.http import DirectResult
        
        from twisted.web2.wsgi import FileWrapper
        
        self.buffer.open()
        body = FileWrapper(self.buffer, 20)
        
        self.buffer.write("<html><body>")
        headers = [('Content-Type', 'text/html')]
        return DirectResult(body, headers)
        
    def writeEvent(self, data) :
        """ Default implementation of a write operation
            to a shared stream.
        """
        
        self.buffer.write('<p>' + data + '</p>')
    
    def closeStream(self) :
        """ Default implementation of a write operation
            to a shared stream.
        """
        self.buffer.close()
