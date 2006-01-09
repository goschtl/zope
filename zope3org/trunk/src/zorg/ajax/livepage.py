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
from zorg.ajax.page import AjaxPage


from zorg.ajax.interfaces import ILiveChanges
from zorg.ajax.interfaces import ILivePage
from zope.publisher.http import DirectResult

from twisted.web2.wsgi import FileWrapper


### Experimental Stuff ###


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


# A global caches dictionary shared between threads
globalClients = {}
from thread import allocate_lock

# A writelock for clients dictionary
writelock = allocate_lock()

# A counter for client ids and its lock
client_id_counter = 0
client_id_writelock = allocate_lock()
            

class LivePageClient(object):
    """An object which represents the client-side webbrowser of a LivePage.
    """

    refreshInterval = 30
    targetTimeoutCount = 3
    
    def __init__(self, livepage) :
       
        client_id_writelock.acquire()
        try:
            global client_id_counter
            self.handleid = str(client_id_counter)
            client_id_counter +=1
        finally:
            client_id_writelock.release()
      
        writelock.acquire()
        try:
            global globalClients
            if self.handleid not in globalClients:
                globalClients[self.handleid] = self
        finally:
            writelock.release()
      
        self.output = [] # IterBuffer()
        
        
class LivePage(AjaxPage) :
    """ A Zope3 substitute for the newov.livepage.LivePage    
    
    The initial call of a LivePage without parameters returns an
    iterable ILivePageResult that allows the browser to ask for a new client:
    
    >>> request = TestRequest()
    >>> page = LivePage(None, request)
    >>> print page.liveChanges()
    <html>
        <head>
            <script type="text/javascript">var nevow_clientHandleId = '0';</script>
            <script src="http://127.0.0.1/nevow_glue.js" type="text/javascript"></script>
        </head>
        <body>
        <p>Input some text.</p>
        <input onchange="server.handle('alert', this.value)" type="text" />
        </body>
    </html>
    
    >>> page = LivePage(None, request)
    >>> print page.liveChanges()
    <html>
        <head>
            <script type="text/javascript">var nevow_clientHandleId = '1';</script>
            <script src="http://127.0.0.1/nevow_glue.js" type="text/javascript"></script>
        </head>
        <body>
        <p>Input some text.</p>
        <input onchange="server.handle('alert', this.value)" type="text" />
        </body>
    </html>
  
    After that the page can be called by the javascript glue as follows
        
    -  liveChanges?livepage_client=new
    
       This creates a new client object on the server side.
    
    -  liveChanges?livepage_client=0&mode=output&outputNum=0
    
       Call the output method and ask for special output that is intended
       for the specified client
   
    -  liveChanges?livepage_client=0&mode=input&handler-path=
        &handler-name=change&arguments=42
        
       Call an input method that produces output for various clients.
      

    Immediately after that we open an output stream :
    
    >>> args=dict(livepage_client=0, mode='output', outputNum=0)
    >>> request = TestRequest(form=args)
    >>> page = LivePage(None, request)
    >>> output = page.liveChanges(debug=False)
  
    Let's try the new client's input and output methods :
    
    >>> args=dict(livepage_client=0, mode='input', handler_name='alert',
    ...                 arguments=42)
    
    >>> request = TestRequest(form=args)
    >>> page = LivePage(None, request)
    >>> page.liveChanges(debug=False)
    'ok'
    
    The iterable output returns javascript snippets:
        
    >>> for chunk in output.body :
    ...     print chunk
    <script type="text/javascript">alert(42)</script>

    And this again and again if we provide new input :
    
    >>> args=dict(livepage_client=0, mode='input', handler_name='alert',
    ...                 arguments=43)
    >>> request = TestRequest(form=args)
    >>> page = LivePage(None, request)
    >>> page.liveChanges(debug=False)
    'ok'
    
    >>> for chunk in output.body :
    ...     print chunk
    <script type="text/javascript">alert(43)</script>

    """
    
    path = os.path.join(os.path.dirname(__file__), "javascript", "nevow_glue.js")    
        
    
    implements(ILivePage)
  
    

    clientFactory = LivePageClient
    answer = None              # special object for input and output requests
                                               
    def renderGlue(self) :
        """ Returns the JavaScript glue.         
        """       
        
        return open(self.path).read()

    def glueURL(self) :
        return zapi.absoluteURL(self.context, self.request) + "/nevow_glue.js"
    
    def clientDict(self) :
        """ Returns a traversable dict of clients. """
        return ITraversable(self.clientFactory)
               
    def nextClientId(self) :
        """ Returns a new client id. """
        
        return self.clientFactory(self).handleid
                 
    def liveChanges(self, debug=False) :
        """ The main response method: returns the HTML that is necessary
            to build up a browser client.
           
            Returns input or output call results if a client and interaction 
            mode is specified.
       
        """
        global globalClients
        if debug :
            import pdb; pdb.set_trace()
            
        client = self.parameter('livepage_client')
        if client is not None :
          
            client = globalClients[str(client)]
            mode = self.parameter('mode')
            if mode == 'input' :
                handler = self.parameter('handler_name')
                arguments = self.parameter('arguments')
                return self.processInput(handler, arguments)
            elif mode == 'output' :
                num = self.parameter('outputNum', type=int)
                return self.processOutput(client, num)
                # output = client.output
#                     output.open()
#                     headers = [('content-type', 'text/html')]
#                     body = FileWrapper(output, 300)
#                     return DirectResult(body, headers)
            else :
                raise RuntimeError, "undefined client mode"
                    
        return self.renderBody()

    def processOutput(self, client, num) :
        end = time.time() + client.refreshInterval
        while time.time() < end :
            if client.output :
                return "alert('output %s')" % client.output.pop()
            time.sleep(0.1)
        return ""
        
    def processInput(self, handler, arguments) :
        global globalClients
        js = getattr(self, handler)(arguments)
        output = js # u'<script type="text/javascript">%s</script>' % js
        for client in globalClients.values() :
            client.output.append(output)
            #client.output.write(output)
        return "alert('input');"
        
    def alert(self, arguments) :
        return "alert(%s)" % arguments
    
    
    def renderBody(self) :
        """ A test method that calls nevow.
        """
        
        template = Template("""<html>
    <head>
        <script type="text/javascript">var nevow_clientHandleId = '$id';</script>
        <script src="$glue" type="text/javascript"></script>
    </head>
    <body>
    <p>Input some text.</p>
    <input onchange="server.handle('alert', this.value)" type="text" />
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