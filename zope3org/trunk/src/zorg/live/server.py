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

$Id: server.py 39651 2005-10-26 18:36:17Z oestermeier $
"""
import doctest, unittest
import time, cgi

from twisted.web2.channel.http import HTTPFactory
from twisted.web2.wsgi import WSGIResource
from twisted.web2.wsgi import WSGIHandler
from twisted.web2.log import LogWrapperResource
from twisted.web2.server import Site
from twisted.web2.iweb import IRequest

from twisted.internet import reactor
from twisted.web2 import stream

from zope.app.wsgi import WSGIPublisherApplication
from zope.app.twisted.server import ServerType
from zope.app.twisted.http import Prebuffer

from zope.publisher.http import DirectResult

from zope.app import zapi
        
from zorg.live.page.interfaces import ILivePageManager
from zorg.live.page.event import IdleEvent
from zorg.live.page.event import ErrorEvent
from zorg.live.page.event import dict2event


class ExtractionError(Exception) :
    """ Indicates a failed searach for a URI part. """
        

class Extractor(object) :
    """ helper fo extracting uuids from a URI. """
    
    def __init__(self, handler) :
        self.context = handler
        
    def extractUUID(self, uri, key) :
        """ Extracts the uuid from the livepage call or raises an IndexError
        
        >>> extract = Extractor(None)
        >>> extract.extractUUID("/exp/@@output/uuid", 'output')
        'uuid'
        
        >>> extract.outputUUID("/exp/@@out/uuid", 'output')
        Traceback (most recent call last):
        ...
        ExtractionError
        
        """
        try :
            return uri.split("/@@%s/" % key)[1].split("?")[0]
        except IndexError :
            raise ExtractionError
    
    def cachedUUID(self, uri) :
        """ Extracts the uuid from the livepage call or raises an IndexError
        
        >>> extract = Extractor(None)
        >>> extract.cachedUUID("/exp/imageMap/cached=uuid")
        'uuid'
        
        >>> extract.cachedUUID("/exp/@@out/uuid")
        Traceback (most recent call last):
        ...
        ExtractionError
        
        """
        splitted = uri.split("cached=")
        if len(splitted) < 2 :
            raise ExtractionError
        try : 
            return splitted[-1].split("&")[0]
        except IndexError :
            raise ExtractionError
            
    def readEvent(self) :
        """ Deserializes the event from the input stream. """
        input = str(self.context.request.stream.read())
        args = cgi.parse_qs(input)
        print "Input", input, args
        for k, v in args.items() :
            args[k] = v[0]
        return dict2event(args)         
                            
    def parseURI(self, uri) :
        """ Checks whether we have a livepage request. """
              
        manager = zapi.getUtility(ILivePageManager)
        handler = self.context
        
        if "/@@output/" in uri :
            try :
                uuid = handler.uuid = self.extractUUID(uri, 'output')
                handler.client = manager.get(uuid, None)
                if handler.client :
                    handler.liverequest = True
            except ExtractionError :
                pass
         
        if "/@@input/" in uri :
            try :
                uuid = handler.uuid = self.extractUUID(uri, 'input')
                client = manager.get(uuid, None)
                if client :
                    event = self.readEvent()
                    if event :
                        client.input(event)
                        ok = DirectResult(("ok",))
                        handler.result = ok
            except ExtractionError :
                pass
       
         
        if "cached=" in uri :
            try :
                uuid = handler.uuid = self.cachedUUID(uri)
                handler.result = manager.fetchResult(uuid, clear=True)
                if handler.result :
                    handler.liverequest = True
            except ExtractionError :
                pass
 
        handler.liverequest = handler.client or handler.result
        return handler.liverequest
  
 
class LivePageWSGIHandler(WSGIHandler) :
    
    idleInterval = 0.2
    limit = 30
    
    count = 0
    client = None
    result = None
    liverequest = False
    
    def __init__(self, application, ctx) :
        super(LivePageWSGIHandler, self).__init__(application, ctx)
        Extractor(self).parseURI(self.request.uri)
        LivePageWSGIHandler.count += 1
        self.num = LivePageWSGIHandler.count
        self.manager = zapi.getUtility(ILivePageManager)

                
    def runLive(self) :
        self.expires = time.time() + self.limit
        reactor.callLater(self.idleInterval, self.onIdle)

 
    def returnResult(self, output, headers=None) :
        """ Writes the result to the deferred response and closes
            the output stream.
        """
        if not headers :
            headers = [('Cache-Control', 'no-store, no-cache, must-revalidate'),
                        ("Connection", "close"),
                        ('content-type', 'text/html;charset=utf-8'), 
                        ('content-length', len(output))]
                                        
        print "***LivePage result", self.num, len(output), "bytes", self.uuid, headers
        print "Output", output
        
        self.startWSGIResponse('200 Ok', headers)
       
        self.headersSent = True
        
        self.response.stream=stream.ProducerStream()
        self.response.stream.write(output)
        self.response.stream.finish()
            
        self.responseDeferred.callback(self.response)
        self.responseDeferred = None
 
 
    def onIdle(self) :
        """ Idle handler that is called by the reactor.
        
            Waits for client specific LivePage output and 
            returns if some output is available.
            
            Returns 'idle' after the timeout if nothing is available.
        """
        
        client = self.manager.get(self.uuid, None)
        if client is None : # Uups, the client has gone in the meanwhile
            error = ErrorEvent(description="Unexpected timeout")
            return self.returnResult(str(error))        
            
        r = self.result
        if r :
            data = ""
            for x in r.body :
                data += x    
            return self.returnResult(data, r.headers)
            
        event = client.nextEvent()
        if event is not None :
            return self.returnResult(str(event))
        
        if time.time() > self.expires :
            return self.returnResult(str(IdleEvent()))
        
        reactor.callLater(self.idleInterval, self.onIdle)
 
 
class LivePageWSGIResource(WSGIResource) :
    """ A special WSGIResource that handles LivePage calls
        more efficiently than Zope.
    """
     
    livepage_handler = None
    
    def __init__(self, application) :
        super(LivePageWSGIResource, self).__init__(application)        
        
    def renderHTTP(self, ctx):
        """ This method creates a special WSGIHandler that for each
            request. Otherwise it mimics exactly the behavior of
            its superclass method.
        """
       
        from twisted.internet import reactor
        # Do stuff with WSGIHandler.
        
        handler = LivePageWSGIHandler(self.application, ctx)
        d = handler.responseDeferred
        if handler.liverequest :
            # A livepage is not called in it's own thread
            handler.runLive()
            return d
        else :
            # Run it in a thread
            reactor.callInThread(handler.run)
            return d

class LiveLogWrapperResource(LogWrapperResource) :
    """ A special LogWrapperResource that does not log LivePage calls.
    """
        
#     
#     def hook(self, ctx):
#         
#         class Dummy(object) :
#             client = None
#             result = None
#             livepage = False
#         
#         request = IRequest(ctx)
#         live = Extractor(Dummy()).parseURI(request.uri)
#         print "hook", request.uri, live
#         if not live :
#             LogWrapperResource.hook(self, ctx)    



def createHTTPFactory(db):

    #print "createHTTPFactory called"
    resource = WSGIPublisherApplication(db)
    resource = LivePageWSGIResource(resource)
    resource = LiveLogWrapperResource(resource)
    resource = Prebuffer(resource)
    return HTTPFactory(Site(resource))


liveServerType = ServerType(createHTTPFactory, 10080)
        
           
