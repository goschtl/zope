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
import time, cgi, os, logging

from twisted.web2.channel.http import HTTPFactory
from twisted.web2.wsgi import WSGIResource
from twisted.web2.wsgi import WSGIHandler
from twisted.web2.log import LogWrapperResource
from twisted.web2.server import Site
from twisted.web2.iweb import IRequest

from twisted.internet import reactor
from twisted.web2 import stream

from zope.component import ComponentLookupError
from zope.interface import implements
from zope.interface import alsoProvides

from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
from zope.app.wsgi import WSGIPublisherApplication
from zope.app.twisted.server import ServerType
from zope.app.twisted.http import Prebuffer

from zope.publisher.http import DirectResult

from zope.app import zapi
        
from zorg.live.page.interfaces import ILivePageManager
from zorg.live.page.interfaces import IIdleEvent

from zorg.live.page.event import IdleEvent
from zorg.live.page.event import ErrorEvent
from zorg.live.page.event import ProgressEvent
from zorg.live.page.event import dict2event

import interfaces


logger = logging.getLogger('zorg.live.server')


badRequest = object()
securityInputLimit = 64000
requestTimeOut = 5

timeout = os.getenv('LIVESERVER_TIMEOUT')
if timeout:
    requestTimeOut = int(timeout)


class ExtractionError(Exception) :
    """ Indicates a failed search for a URI part. """
        
class InputLimitExceeded(Exception) :
    """ Indicates an input that exceeds the security limit. """


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
    
    def queryUUID(self, uri, key) :
        """ Extracts the uuid from the livepage call or raises an IndexError
        
        >>> extract = Extractor(None)
        >>> extract.queryUUID("/exp/imageMap/cached=uuid", "cached")
        'uuid'
        
        >>> extract.queryUUID("/exp/@@out/uuid", "cached")
        Traceback (most recent call last):
        ...
        ExtractionError
        
        """
        splitted = uri.split(key + "=")
        if len(splitted) < 2 :
            raise ExtractionError
        try : 
            return splitted[-1].split("&")[0]
        except IndexError :
            raise ExtractionError
                  
    def readEvent(self) :
        """ Deserializes the event from the input stream. """
        global securityInputLimit
        
        stream = self.context.request.stream
        input = str(stream.read())
        if len(input) > securityInputLimit :
            return None                 # indicates a bad request
        
        args = cgi.parse_qs(input)
        
        for k, v in args.items() :
            args[k] = v[0]
        try :
            event = dict2event(args)
            logger.log(logging.INFO,"Input %s" % (event))
            return event
        except ComponentLookupError :
            logger.warning("Cannot parse event %s" % (args))
            return None                     
            
        
                            
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
                    else :
                        global badRequest
                        handler.result = badRequest
                        
                        
            except ExtractionError :
                pass
       
        if "cached=" in uri :
            try :
                uuid = handler.uuid = self.queryUUID(uri, "cached")
                handler.result = manager.fetchResult(uuid, clear=True)
                if handler.result :
                    handler.liverequest = True
            except ExtractionError :
                pass
 
        handler.liverequest = handler.client or handler.result
        return handler.liverequest
  
 
class LivePageWSGIHandler(WSGIHandler) :
    
    idleInterval = 0.1

    count = 0
    client = None
    result = None
    liverequest = False
    exceeded = False
    
    def __init__(self, application, ctx) :
        super(LivePageWSGIHandler, self).__init__(application, ctx)
        Extractor(self).parseURI(self.request.uri)
        LivePageWSGIHandler.count += 1
        self.num = LivePageWSGIHandler.count
        self.manager = zapi.getUtility(ILivePageManager)

                
    def runLive(self) :
        global requestTimeOut
        self.expires = time.time() + requestTimeOut
        reactor.callLater(self.idleInterval, self.onIdle)

    def _returnOutput(self, output) :
        self.headersSent = True
        
        self.response.stream=stream.ProducerStream()
        self.response.stream.write(output)
        self.response.stream.finish()
            
        self.responseDeferred.callback(self.response)
        self.responseDeferred = None
        
    
    def returnError(self, error) :
        """ Writes an error result. """
        self.startWSGIResponse(error, [])
        self._returnOutput("")        
        
    def returnResult(self, output, headers=None) :
        """ Writes the result to the deferred response and closes
            the output stream.
        """
        if not headers :
            headers = [('Cache-Control', 'no-store, no-cache, must-revalidate'),
                        ("Connection", "close"),
                        ('content-type', 'text/html;charset=utf-8'), 
                        ('content-length', len(output))]
        
        self.startWSGIResponse('200 Ok', headers)
        self._returnOutput(output)
        
    def onIdle(self) :
        """ Idle handler that is called by the reactor.
        
            Waits for client specific LivePage output and 
            returns if some output is available.
            
            Returns 'idle' after the timeout if nothing is available.
        """
        
        client = self.manager.get(self.uuid, None)
        if client is None : # Uups, the client has gone in the meanwhile
            error = ErrorEvent(description="Unexpected timeout")
            return self.returnResult(error.toJSON())        
            
        r = self.result
        if r == badRequest :
            return self.returnError('400 Bad Request')
        if r :
            data = ""
            for x in r.body :
                data += x    
            return self.returnResult(data, r.headers)
            
        event = client.nextEvent()
        if event is not None :
            json = event.toJSON()
            if not IIdleEvent.providedBy(event) :
                logger.log(logging.INFO, "Sending... %s" % (json))
        
            return self.returnResult(json)
        
        if time.time() > self.expires :
            return self.returnResult(IdleEvent().toJSON())
        
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
        
        # reactor.threadpool.dumpStats()
        
        handler = LivePageWSGIHandler(self.application, ctx)
        d = handler.responseDeferred
        if handler.liverequest :
            # Run outside thread
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


from cStringIO import StringIO
import tempfile
from twisted.web2 import iweb, resource, stream


class LiveInputStream(object) :
    """ A wrapper for live input streams. This wrapper
        can report the progress of the upload tasks or prevent 
        a malevolent upload.
    """
    
    exceeded = False
    
    def __init__(self, stream, client=None, content_length=None, type=None) :
        self.stream = stream
        self.received_bytes = 0
        self.expected_length = content_length or 1.0
        self.client = client
        self.reported = time.time()
        self.interval = LivePageWSGIHandler.idleInterval * 2
        self.type = type
        
    def write(self, data) :
        global securityInputLimit
        self.received_bytes += len(data)
        if not self.exceeded :
            self.stream.write(data)
        
        if self.client is not None:

            if self.type == "progress" :
                if time.time() > (self.reported + self.interval) :
                    ratio = float(self.received_bytes) / float(self.expected_length)
                    percent = int(ratio * 100.0)
                    
                    who = self.client.principal.id
                    event = ProgressEvent(percent=percent, recipients=[who])
                    manager = zapi.getUtility(ILivePageManager)
                    manager.addEvent(event)
                    
                    self.reported = time.time()
                    
            elif self.type == "input" :
                if self.received_bytes > securityInputLimit :
                    self.exceeded = True
                    
                    
    
class LivePrebuffer(resource.WrapperResource):

    max_stringio = 100*1000 # Should this be configurable?

    def hook(self, ctx):
        req = iweb.IRequest(ctx)

        content_length = req.headers.getHeader('content-length')
        if content_length is not None and \
                        int(content_length) > self.max_stringio:
            temp = tempfile.TemporaryFile()
            def done(_):
                temp.seek(0)
                # Replace the request's stream object with the tempfile
                req.stream = stream.FileStream(temp, useMMap=False)
                # Hm, this shouldn't be required:
                req.stream.doStartReading = None

        else:
            temp = StringIO()
            def done(_):
                # Replace the request's stream object with the tempfile
                req.stream = stream.MemoryStream(temp.getvalue())
                # Hm, this shouldn't be required:
                req.stream.doStartReading = None
        
        manager = zapi.getUtility(ILivePageManager)
        extractor = Extractor(ctx)
        type = None
        client = None
        try :
            uuid = extractor.queryUUID(req.uri, "progress")
            type = "progress"
        except ExtractionError :
            uuid = None
        
        if not uuid :
            try :
                uuid = extractor.extractUUID(req.uri, "input")
                type = "input"
            except ExtractionError :
                uuid = None
            
        if uuid :
            client = manager.get(uuid)
        
        live = LiveInputStream(temp, client, content_length, type)
        
        return stream.readStream(req.stream, live.write).addCallback(done)

    # Oops, fix missing () in lambda in WrapperResource
    def locateChild(self, ctx, segments):
        x = self.hook(ctx)
        if x is not None:
            return x.addCallback(lambda data: (self.res, segments))
        return self.res, segments


class HTTPLivePageRequestFactory(HTTPPublicationRequestFactory) :
    """ A special request factory for live page servers. 
        Marks all requests as live page requests.
    """
    
    def __call__(self, input_stream, env, output_stream=None) :
        request = super(HTTPLivePageRequestFactory, self).__call__(input_stream,
                                                            env, output_stream)
        alsoProvides(request, interfaces.ILiveRequest)       
        return request
        

    
def createHTTPFactory(db):

    reactor.threadpool.adjustPoolsize(10, 20)
    
#     manager = zapi.getUtility(ILivePageManager)
#     manager.connect(db)
    
    resource = WSGIPublisherApplication(db, factory=HTTPLivePageRequestFactory)
    resource = LivePageWSGIResource(resource)
    resource = LiveLogWrapperResource(resource)
    resource = LivePrebuffer(resource)
    return HTTPFactory(Site(resource))


liveServerType = ServerType(createHTTPFactory, 10080)
        
           
