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

$Id: view.py 39651 2005-10-26 18:36:17Z oestermeier $
"""
__docformat__ = 'restructuredtext'

import os, itertools, unittest
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

from zope.app.traversing.interfaces import TraversalError
from zope.app.traversing.interfaces import ITraversable
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.app.publisher.browser import BrowserView

from zope.interface import implements
from zope.interface import Interface
from zorg.ajax.page import AjaxPage


from zorg.ajax.interfaces import ILiveChanges


### Experimental Stuff ###


class IIterable(Interface) :
    
    def __iter__() :
        """ Defines an iterable. """


class FileBuffer(object):
    """ A buffer for shared read and write operations. """
    closed = False
    count = 0
    
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
        print "."
        return '\n<p>.</p>'
        
    def __iter__(self) :
        data = self.read(100)
        if data is None :
            raise StopIteration
        return data
            
    def close(self) :
        self.write("</body></html>")
        self.closed = True
  
    def open(self) :
        self.closed = False
        self.count = 0

from zope.interface import Interface

class IIterable(Interface) :
    
    def __iter__() :
        """ Defines an iterable. """
        
class IterBuffer(object) :

    implements(IIterable)
    
    count = 0
    stop = False
    
    def __init__(self):
        self.buf = ''

    def write(self, str):
        self.buf += str

    def close(self) :
        self.write("</body></html>")
        self.stop = True
         
    def __iter__(self) :
        data = self.buf
        if data :
            self.buf = ''
            return data
        self.count += 1
        time.sleep(0.1)
        
        if self.count > 100 :
            self.close()
            
        if self.stop :
            raise StopIteration
            
    def next(self) :
        try :
            return self.__iter__()
        except StopIteration :
            return None
        
            
    
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
        
        from zope.publisher.interfaces.http import IResult
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


class LivePageClient(object):
    """An object which represents the client-side webbrowser.
    """

    refreshInterval = 30
    targetTimeoutCount = 3
    
    def __init__(self, livepage) :
        self.livepage = livepage
        self.handleid = str(itertools.count().next())
        livepage.clients[self.handleid] = self
        
class LivePage(AjaxPage) :
    """ A Zope3 substitute for the newov.livepage.LivePage    
    
        The page is called by the javascript glue as follows
        
        liveChanges/livepage_client/0/output?
        
        liveChanges/livepage_client/0/input?handler-path=&handler-name=change&arguments=sadas
    
        >>> request = TestRequest()
        >>> page = LivePage(None, request)
        
        The renderBody method creates a new client:
        
        >>> print page.renderBody()
        <html>
            <head>
                <script type="text/javascript">var nevow_clientHandleId = '0';</script>
                <script src="http://127.0.0.1/nevow_glue.js" type="text/javascript"></script>
            </head>
            <body>
            <p>Input some text.</p>
            <input onchange="server.handle('change', this.value)" type="text" />
            </body>
        </html>
       
        After that we can access the new client's input and output resources :
        
        >>> clients = page.publishTraverse(request, u'livepage_client')
        >>> resources = clients.publishTraverse(request, u'0')
        >>> output = resources.publishTraverse(request, u'output')
        >>> input = resources.publishTraverse(request, u'output')
        
        The output resource returns javascript snippets:
        
        /liveChanges/livepage_client/0/output?outputNum=0
        
        
        

    """
    
    path = os.path.join(os.path.dirname(__file__), "javascript", "nevow_glue.js")    
        
    
    implements(IPublishTraverse)
  
    clientFactory = LivePageClient
    clients = {}
    
    def __init__(self, context, request) :    
        self.context = context
        self.request = request
        
    def publishTraverse(self, request, name) :
        if name == u'livepage_client' :
            return LivePageClients(self)
            
        raise NotFound(self, name, request)
        
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
                
    
    def renderBody(self) :
        """ A test method that calls nevow.
        
        >>> page = LivePage(None, TestRequest())
        >>> print page.renderBody()
        <html>
            <head>
                <script type="text/javascript">var nevow_clientHandleId = '0';</script>
                <script src="http://127.0.0.1/nevow_glue.js" type="text/javascript"></script>
            </head>
            <body>
            <p>Input some text.</p>
            <input onchange="server.handle('change', this.value)" type="text" />
            </body>
        </html>
        
        
        """
        
        template = Template("""<html>
    <head>
        <script type="text/javascript">var nevow_clientHandleId = '$id';</script>
        <script src="$glue" type="text/javascript"></script>
    </head>
    <body>
    <p>Input some text.</p>
    <input onchange="server.handle('change', this.value)" type="text" />
    </body>
</html>""")      
                                                
        return template.substitute(id=self.nextClientId(), glue=self.glueURL())
 
 
    def this(self) :
        return self
              
    def handle_change(self, ctx, value):
        import pdb; pdb.set_trace()
        
        return livepage.alert(value)

defineChecker(LivePage, NoProxy)

class Contextual(object) :
    """  Convenient super class for wrapper and adapter. """
    def __init__(self, context) :
        self.context = removeSecurityProxy(context)
        
class LivePageResult(Contextual) :
    """ An adapter that converts a LivePage into an IResult. """

    from zope.publisher.interfaces.http import IResult
    
    implements(IResult)
    adapts(LivePage)
    
    headers = ()
        
    def getBody(self) :
        return (self.context.renderBody(),)  # returns the body
        
    body = property(getBody)

defineChecker(LivePageResult, NoProxy)

class LivePageClients(Contextual) :
    """ A traverser that traverses a dict of clients. """
    
    implements(IPublishTraverse)
           
    def publishTraverse(self, request, name) :  
        try :
            client = self.context.clients[str(name)]
            return ClientResources(client)
        except KeyError :
            raise NotFound(self, name, request)

defineChecker(LivePageClients, NoProxy)

class InputResource(Contextual) :
    pass

defineChecker(InputResource, NoProxy)

class OutputResource(Contextual) :
    
    
    def __call__(self, *args) :
        print args
        return "ok"

defineChecker(OutputResource, NoProxy)


class ClientResources(Contextual) :
    """ A traverser that returns an input or an output resource. """
    
    implements(IPublishTraverse)
     
    clientResources = dict(input=InputResource, output=OutputResource)
    
    def publishTraverse(self, request, name) :       
        try :   
            resource = self.clientResources[name]
            return resource(self.context)
        except KeyError :
            raise NotFound(self, name, request)

defineChecker(ClientResources, NoProxy)

