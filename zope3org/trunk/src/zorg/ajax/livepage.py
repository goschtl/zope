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

class LivePageClients(dict) :
    """ A dictionary of LivePageClients with ids as keys and clienst as values.
        Makes all write operations thread safe.
        
    """
    
    implements(ILivePageClients)
    
    writelock = allocate_lock()     # A writelock for clients
   

    def register(self, client, uuid=None) :
        if uuid is None :
            uuid = zapi.getUtility(IUUIDGenerator)()    
        self.writelock.acquire()
        try:
            client.handleid = uuid
            self[client.handleid] = client
        finally:
            self.writelock.release()
                  
    def addOutput(self, output, who="all") :
        if who == "all" :
            for client in clients.values() :
                client.addOutput(output)
            
    def whoIsOnline(self) :
        """ Returns the ids of the principals that are using livepages. """
        online = set()
        for client in self.values() :
            online.add(client.principal.id)
        return sorted(online)
        
            

def livePageSubscriber(event) :
    """ A subscriber that allows the clients to respond to
        Zope3 events.
    """
    global clients
    for client in clients.values() :
        client.notify(event)

                     
       
# A global dictionary shared between threads
clients = LivePageClients()



class LivePageClient(object):
    """An object which represents the client-side webbrowser of a LivePage.
    """

    implements(ILivePageClients)
    
    refreshInterval = 30
    targetTimeoutCount = 3
    
    def __init__(self, page, uuid=None) :
        global clients
        if uuid is None :
            clients.register(self)
        self.page_class = page.__class__
        self.output = []
        self.principal = page.request.principal
        self.writelock = allocate_lock()
        
    def notify(self, event) :
        self.page_class.notify(event)
   
    def popOutput(self) :
        self.writelock.acquire()
        try :
            if self.output :
                result = self.output.pop()
            else :
                result = None
        finally :
            self.writelock.release()
        return result
    
    def addOutput(self, output) :
        self.writelock.acquire()
        try:
            if output not in self.output :
                self.output.append(output)
        finally:
            self.writelock.release()


        
class LivePage(ComposedAjaxPage) :
    """ A Zope3 substitute for the newov.livepage.LivePage    
    
    The initial call of a LivePage (without parameters) returns a page
    that immediately connects a client to the server. After that the client
    asks again and again for new available output. The output consists of 
    JavaScript snippets that are evaluated by the browser.
    
    Here we simulate the startup of two clients:
    
    >>> class Principal(object) :
    ...     def __init__(self, id, title) :
    ...         self.id = id
    ...         self.title = title
    
    >>> user1 = Principal('zorg.member.uwe', u'Uwe Oestmeier')
    >>> user2 = Principal('zorg.member.dominik', u'Dominik Huber')
    
    >>> request = TestRequest()
    >>> request.setPrincipal(user1)
    >>> page = LivePage(None, request)
    >>> print page.render()
    <html>
        <head>
            <script type="text/javascript">var livePageUUID = 'uuid1';</script>
            <script src="http://127.0.0.1/livepage.js" type="text/javascript"></script>
        </head>
        <body>
        <p>Input some text.</p>
        <input onchange="sendLivePage('alert', this.value)" type="text" />
        </body>
    </html>
    
    >>> request.setPrincipal(user2)
    >>> page = LivePage(None, request)
    >>> print page.render()
    <html>
        <head>
            <script type="text/javascript">var livePageUUID = 'uuid2';</script>
            <script src="http://127.0.0.1/livepage.js" type="text/javascript"></script>
        </head>
        <body>
        <p>Input some text.</p>
        <input onchange="sendLivePage('alert', this.value)" type="text" />
        </body>
    </html>
    
    The global clients dictionary can be asked for all online users:
    
    >>> clients.whoIsOnline()
    ['zorg.member.dominik', 'zorg.member.uwe']
    
    
    For test purposes we set the refresh interval (i.e. the interval in which
    output calls are renewed) to 0.1 seconds :
    
    >>> for client in clients.values() : 
    ...     client.refreshInterval = 0.1
  
    After that the page can be called by the javascript glue as follows
    
    -  livepageoutput?uuid=uuid0&outputNum=0
    
       Call the output method and ask for special output that is intended
       for the specified client
   
    -  livepageinput?uuid=uuid0&handler-name=change&arguments=42
        
       Call an input method that produces output for various clients.
      
    After the startup we ask for some output. Since nothing happened, the
    output is 'idle':
    
    >>> page1 = LivePage(None, TestRequest())
    >>> page1.output(uuid='uuid1', outputNum=0)
    'idle'
  
    Now we can send some input :
    
    >>> page2 = LivePage(None, TestRequest())
    >>> page2.input(uuid='uuid1', handler_name='alert', arguments=42)
    ''
    
    After that the next call of the output returns javascript snippets:
        
    >>> page1.output(uuid='uuid1', outputNum=1)
    "javascript alert('42')"

    And this again and again if we provide new input :
    
    >>> page2.input(uuid='uuid1', handler_name='alert', arguments=43)
    ''
    
    >>> page1.output(uuid='uuid1', outputNum=2)
    "javascript alert('43')"

    """
    
    path = os.path.join(os.path.dirname(__file__), "javascript", "livepage.js")    
        
    
    implements(ILivePage)
  
    clientFactory = LivePageClient

                                               
    def renderGlue(self) :
        """ Returns the JavaScript glue.         
        """       
        
        return open(self.path).read()
        
    def notify(self, event) :
        """ Default implementation of an event handler. Must be specialized. """
        pass

    def glueURL(self) :
        return zapi.absoluteURL(self.context, self.request) + "/livepage.js"
                   
    def nextClientId(self) :
        """ Returns a new client id. """
        
        return self.clientFactory(self).handleid

    def output(self, uuid, outputNum) :
        """ Returns the output of a single client. """
        global clients
        client = clients.get(uuid)
        if client is None :
            client = self.clientFactory(self, uuid)
            clients.register(client, uuid)
        
        end = time.time() + client.refreshInterval
        while time.time() < end :
            output = client.popOutput()
            if output :
                return output
            time.sleep(0.1)
        return "idle"
        
    def input(self, uuid, handler_name, arguments) :
        return self.sendResponse(getattr(self, handler_name)(arguments))
        
    def sendResponse(self, response) :
        """ Sends a livepage response to all clients. 
            A response consits of a leading command line 
            and optional html body data.
        """
        global clients
        clients.addOutput(response)
        return ''
        
    sendResponse = classmethod(sendResponse)  
    
    def alert(self, arguments) :
        return "javascript alert('%s')" % arguments
        
    def update(self, arguments) :
        return "javascript update('%s')" % arguments
    
    def render(self) :
        """ A test method that calls the livepage. 
            
            Must be overwritten. The method must call self.nextClientId to
            ensure that a unique key is generated.
            
        """
        
        template = Template("""<html>
    <head>
        <script type="text/javascript">var livePageUUID = '$id';</script>
        <script src="$glue" type="text/javascript"></script>
    </head>
    <body>
    <p>Input some text.</p>
    <input onchange="sendLivePage('alert', this.value)" type="text" />
    </body>
</html>""")      
                                                
        return template.substitute(id=self.nextClientId(), glue=self.glueURL())
 

defineChecker(LivePage, NoProxy)
        
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
