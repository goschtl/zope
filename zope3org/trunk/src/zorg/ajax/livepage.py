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

import os, itertools, unittest, time, transaction
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


class Cache(object) :
    """ Simple cache that uses least recently accessed time to trim size """

    def __init__(self, size=100):
        self.data = {}
        self.size = size

    def resize(self):
        """ trim cache to no more than 95% of desired size """
        trim = max(0, int(len(self.data)-0.95*self.size))
        if trim:
            # don't want self.items() because we must sort list by access time
            values = map(None, self.data.values(), self.data.keys())
            values.sort()
            for val,k in values[0:trim]:
                try :
                    del self.data[k]
                except KeyError:
                    pass
                    
    def __delitem__(self, key) :
        try :
            del self.data[key]
        except KeyError:
            pass

    def __setitem__(self,key,val):
        if (not self.data.has_key(key) and
        len(self.data) >= self.size):
            self.resize()
        self.data[key] = (time.time(), val)

    def __getitem__(self,key):
        """ like normal __getitem__ but updates time of fetched entry """
        val = self.data[key][1]
        self.data[key] = (time.time(),val)
        return val

    def get(self,key,default=None):
        """ like normal __getitem__ but updates time of fetched entry """
        try :
            return self[key]
        except KeyError:
            return default


class LivePageClients(object) :
    """ Groups collections of LivePages.
    
        Holds a dict of dict of LivePageClients with group_ids and
        client uuids as keys and clients as values.
        
        Makes all write operations thread safe.
    """
    
    implements(ILivePageClients)
    
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
        
        >>> clients = LivePageClients()
        >>> uuid = clients.cacheResult(42)
        >>> clients.fetchResult(uuid)
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

        >>> clients = LivePageClients()
        >>> uuid = clients.cacheResult(42)
        >>> clients.fetchResult(uuid)
        42

        """
        result = self.results.get(uuid, None)
        if clear :
            del self.results[uuid]
        return result
        
    def _group(self, group_id) :
        """ Internal method that returns a dict of uuid, client tuples
            that belong to a group specified by a group id.
            
        >>> clients = LivePageClients()
        >>> clients._group(42)
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
            print "whoIsOnline", group_id, client.principal.id
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
    
    refreshInterval = 10    # seconds
    targetTimeout = 20
    
    def __init__(self, page, uuid=None) :
        global clients
        self.group_id = page.getGroupId()
        self.page_class = page.__class__
        self.outbox = []
        self.principal = page.request.principal
        self.writelock = allocate_lock()
        self.touched = time.time()
        clients.register(self, uuid)
            
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
    
    >>> for client in clients :
    ...     print client.principal.id
    zorg.member.dominik
    zorg.member.uwe
    
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
        #print "***nextClientId called"
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
 
    def sendResponse(cls, response, group_id, recipients="all") :
        """ Sends a livepage response to all clients. 
            A response consits of a leading command line 
            and optional html body data.
        """
        global clients
        assert isinstance(response, str)
        clients.addOutput(response, group_id, recipients)
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
        return client       
            
class Output(ClientIO) :
    """ A view of a LivePage view that allows to traverse to a specific
        client.
        
    """
    
    implements(IPublishTraverse)
      
    def publishTraverse(self, request, uuid) :
        #print "Output call", request.URL, uuid
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
