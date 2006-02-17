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

from zope.app import zapi

from zorg.live.page.interfaces import ILivePageManager

class ExtractionError(Exception) :
    """ Indicates a failed searach for a URI part. """
        

class Extractor(object) :
    """ helper fo extracting uuids from a URI. """
    
    def __init__(self, handler) :
        self.context = handler
        
    def extractUUID(self, uri, key) :
        """ Extracts the uuid from the livepage call or raises an IndexError
        
        >>> extract = Extractor(None)
        >>> extract.extractUUID("/exp/@@output/uuid?outputNum=1", 'output')
        'uuid'
        
        >>> extract.outputUUID("/exp/@@out/uuid?outputNum=1", 'output')
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
        
        >>> extract.cachedUUID("/exp/@@out/uuid?outputNum=1")
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
            
    def parseURI(self, uri) :
        """ Checks whether we have a livepage request. """
              
        manager = zapi.getUtility(ILivePageManager)
        handler = self.context
        
        if "/@@output/" in uri :
            try :
                uuid = handler.uuid = self.extractUUID(uri, 'output')
                handler.client = manager.get(uuid, None)
            except ExtractionError :
                pass
         
#         if "/@@input/" in uri :
#             try :
#                 uuid = handler.uuid = self.extractUUID(uri, 'input')
#                 handler.client = manager.get(uuid, None)
#             except ExtractionError :
#                 pass
                
        if "cached=" in uri :
            try :
                uuid = handler.uuid = self.cachedUUID(uri)
                handler.result = manager.fetchResult(uuid, clear=True)
            except ExtractionError :
                pass
         
        handler.liverequest = handler.client or handler.result
        return handler.liverequest
  
 
class LivePageWSGIHandler(WSGIHandler) :
    
    idleInterval = 0.5
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
                
    def runLive(self) :
        #print "runLive", self.request.uri
        self.expires = time.time() + self.limit
        reactor.callLater(self.idleInterval, self.onIdle)
 
    def returnResult(self, output, headers=None) :
        """ Writes the result to the deferred response and closes
            the output stream.
        """
        print "***LivePage result", self.num, len(output), "bytes", self.uuid, headers
        
        if headers is None :
            headers = [('content-type', 'text/plain;charset=utf-8'), 
                                        ('content-length', len(output))]
        self.startWSGIResponse('200 Ok', headers)
       
        #output = output.replace("\n", "*")
        self.headersSent = True
        
        self.response.stream=stream.ProducerStream()
        self.response.stream.write(output)
        self.response.stream.finish()
            
        #import pdb; pdb.set_trace()
        self.responseDeferred.callback(self.response)
        self.responseDeferred = None
      
       
    def availableOutput(self) :
        """ Checks for available output in the out box of the client. """
        
        return self.client.popOutput()
        
        
    def onIdle(self) :
        """ Idle handler that is called by the reactor.
        
            Waits for client specific LivePage output and 
            returns if some output is available.
            
            Returns 'idle' after the timeout if nothing is available.
        """
        
        r = self.result
        if r :
            data = ""
            for x in r.body :
                data += x    
            return self.returnResult(data, r.headers)
            
        output = self.availableOutput()
        if time.time() > self.expires :
            return self.returnResult(output or "idle\n")
        if output :
            reactor.callLater(0.5, self.returnResult, output)
            #self.returnResult(output)
        else :
            reactor.callLater(self.idleInterval, self.onIdle)
 
                
class LivePageWSGIResource(WSGIResource) :
    """ A special WSGIResource that handles LivePage calls
        more efficiently than Zope.
    """
     
    livepage_handler = None
    
    def __init__(self, application, db) :
        super(LivePageWSGIResource, self).__init__(application)
        self.db = db
        
        
    def renderHTTP(self, ctx):
        """ This method creates a special WSGIHandler that for each
            request. Otherwise it mimics exactly the behavior of
            its superclass method.
        """
        #print "renderHTTP called"
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
    zopeserver = WSGIPublisherApplication(db)
    resource = LivePageWSGIResource(zopeserver, db)
    resource = LiveLogWrapperResource(resource)
    return HTTPFactory(Site(resource))


liveServerType = ServerType(createHTTPFactory, 10080)
        
           
