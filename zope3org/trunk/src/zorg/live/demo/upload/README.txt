Upload Demo
===========

This demo shows how LivePages can be used to provide better feedback to users.
On file upload the user is informed about the progress of the upload task, i.e.
the amout of transfered bytes.


    >>> from zorg.live.page.manager import LivePageManager
    >>> from zorg.live.page.interfaces import ILivePageManager
    >>> manager = LivePageManager()
    >>> zope.component.provideUtility(manager, ILivePageManager)

Additionally we must add a subscriber that observes Zope3 events and 
LivePageEvents :

    >>> from zorg.live.page.manager import livePageSubscriber
    >>> zope.event.subscribers.append(livePageSubscriber)

For test purposes we set the refresh interval (i.e. the interval in which
output calls are renewed) to 0.1 seconds :
    
    >>> from zorg.live.page.client import LivePageClient
    >>> LivePageClient.refreshInterval = 0.1

Now we simulate the startup of a client. We need a folder that allows us
to upload a file and a user :

    >>> from zorg.live.demo.upload.tests import buildTestFolder
    >>> folder = buildTestFolder()
    >>> class Principal(object) :
    ...     def __init__(self, id, title) :
    ...         self.id = id
    ...         self.title = title
    
    >>> user = Principal('zorg.member.uwe', u'Uwe Oestmeier')

Note that the startup is simulated by the nextClientId() call. We need
a second event handler who shows what happens :
    
    >>> def printEvent(event) :
    ...     print "Event:", event.__class__.__name__
    >>> zope.event.subscribers.append(printEvent)
    
And here is the simulated page request that starts the live session:

    >>> from zorg.live.demo.upload.upload import LiveFileAdd
    >>> request = TestRequest()
    >>> request.setPrincipal(user)
    >>> page = LiveFileAdd(folder, request)
    >>> clientID = page.nextClientId()
    Event: LoginEvent
    >>> client = manager.get(clientID)
    
Now we upload the file. If we upload only a small file the view mimics the
standard Add File view:
    
    >>> page.update_object("Some text", "text/plain")
    Event: ObjectCreatedEvent
    Event: ObjectAddedEvent
    Event: ContainerModifiedEvent
    ''
    
The interesting part is handled by the WSGI LivePage server, which buffers
the uploaded file content in an input stream before the actual Zope handler
is called. The progress is reported by a LiveInputStream wrapper that set
up by the request handler. Here we simply simulate such an request by
repeately calling the wrapping write method:

    >>> class DummyStream(object) :
    ...     def write(self, data) : pass
    >>> dummy = DummyStream()
    >>> import time    
    >>> from zorg.live.server import LiveInputStream
    >>> stream = LiveInputStream(dummy, client, content_length=100, 
    ...                                                     type="progress")
    
We need an event logger for progress events:

    >>> def printEvents():
    ...     event = client.nextEvent()
    ...     while event:
    ...         if event.name == "progress" :
    ...             event.pprint()
    ...         event = client.nextEvent()    

Now we simulate repeated write calls:

    >>> for i in range(1, 10) :
    ...     time.sleep(0.1)
    ...     stream.write("Some Data")
    ...     printEvents()
    name : 'progress'
    percent : 18
    recipients : ['zorg.member.uwe']
    where : None
    name : 'progress'
    percent : 36
    recipients : ['zorg.member.uwe']
    where : None
    name : 'progress'
    percent : 54
    recipients : ['zorg.member.uwe']
    where : None
    name : 'progress'
    percent : 72
    recipients : ['zorg.member.uwe']
    where : None

Clean up:

    >>> zope.event.subscribers.remove(livePageSubscriber)
    >>> zope.event.subscribers.remove(printEvent)
