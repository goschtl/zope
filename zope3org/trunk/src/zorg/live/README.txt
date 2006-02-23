====
Live
====

This package is experimental. It contains a LivePage implementation that
is similar to and inspired by Nevows LivePages, see also 

    http://divmod.org/trac/wiki/DivmodNevow
  
Installation
------------

The current implementation runs to a limited degree with Zope3's buildin
servers. To enable LivePages for more users than server threads
you must install the LiveServer that is included in this package. Add the
following lines to your 'zope.conf' file :

    <server>
      type LiveServerHTTP
      address 8088
    </server>



Basic idea
----------

This LivePage package implements a MVC approach in its narrow sense: it uses
server generated events to update browser views in real time.
It tries to  try to overcome the traditional model of web pages in which the
content of the page is only refreshed in response to a user activity. Besides the
typically request response cycle that is under the control of the user
a LivePage opens a background request that waits for notification of server
side events. This background request waits until an event arrives,
performs some a (mostly partial) page update upon notification, and
repeats a new request for further notifications. This means 
that each LivePage constantly opens HTTP channels until an event
arrives, closes the channel and immediately reopens a new channel.


Main problems
------------

Since many events are broadcasted to several users this might lead to massive 
concurrent requests for new events, which start nearly at the same time.

Zope is not well-suited for this performance model since each request is handled
in a seperate thread with its own database connection and object cache. 
For most of the background event polling this is an unnecessary 
overhead that limits the number of connected users to the number of available 
threads. This might work for two or three users but not for 20 users or more 
which are concurrently online and share the same resources.

Therefore this package contains a specialization of Zope3's twisted server
that handles all LivePage requests without the need for database connections  
and persistent objects outside of the ordinary Zope3 threads. 
The Zope3 requests still work of course but should be restricted to security 
or persistence issues as far as possible whereas the event handling is done
by twisted.

Another problem is that the Zope event model does not guarantee that we get
all relevant data to distinguish relevant events. For instance, many Zope
application send many ObjectModifiedEvents after another without distinguishing
between changes of a ZopeDublinCore attribute, the file data, container content,
etc. As long as the ObjectModifiedEvent is only used to update the modification
time of an object this is fine, but in a MVC architecture where the views
must be updated in a more fine graned manner this often leads to redundant
updates of large parts of the page. E.g. if we have a form with the
title, description, and effective date of an object that we want publish,
all slots must be updated in response to an ObjectModifiedEvent as long as
the event does not use the optional modification descriptors, which
are there, but rarely used (This by the way is also a main problem of the 
current Catalog implementation)

In order to ensure that events are not send multiple times we need a
check whether an identical event has already be processed and whether
this really matters. This largeley depends on the application. In a chat
application it might be ok if a single user repeats himself whereas
in a list view of container we must ensure that each object is represented
by only one list item. 
The check for redundant events could be done on the server or on the client
side. We decided to use the client side since it may happen that some
events get lost and redundancy may be usable to recover from such situations.
So we leave the check for redundant events completely to the JavaScript client
which stores update and append operations on DOM elements in a hash.


Usage
-----

LivePages are special BrowserViews that install a LivePageClient on the server
side for each page that is connected to a LiveServer. The LivePageClient
is registered in a central utility, which provides access across requests
to the same global datastructures. It must be ensured that these global data
can be accessed in a thread safe way.

    >>> from zorg.live.page.manager import LivePageManager
    >>> from zorg.live.page.interfaces import ILivePageManager
    >>> manager = LivePageManager()
    >>> zope.component.provideUtility(manager, ILivePageManager)
    
Additionally we must add a subscriber that observes Zope3 events and 
the LivePageEvents :

    >>> from zorg.live.page.manager import livePageSubscriber
    >>> zope.event.subscribers.append(livePageSubscriber)

Now we simulate the startup of two clients.

    >>> from zorg.live.testing import TestLivePage
    
    >>> class Principal(object) :
    ...     def __init__(self, id, title) :
    ...         self.id = id
    ...         self.title = title
    
    >>> user1 = Principal('zorg.member.uwe', u'Uwe Oestmeier')
    >>> user2 = Principal('zorg.member.dominik', u'Dominik Huber')
    
    >>> request = TestRequest()
    >>> request.setPrincipal(user1)
    
    >>> page = TestLivePage(None, request)
    >>> where = page.getLocationId()
    >>> print page.render()
    <html>
        <head>
            <script src="http://127.0.0.1/++resource++zorgajax/prototype.js" type="text/javascript"></script>
            <script type="text/javascript">var livePageUUID = 'uuid1';</script>
            <script src="http://127.0.0.1/++resource++zorgajax/livepage.js" type="text/javascript"></script>
        </head>
        <body onload="startClient()">
        <p>Input some text.</p>
        <input onchange="sendEvent('append', 'target', this.value)" type="text" />
        <p id="target">Text goes here:</p>
        </body>
    </html>

    
    >>> request.setPrincipal(user2)
    >>> page = TestLivePage(None, request)
    >>> print page.render()
    <html>
        <head>
            <script src="http://127.0.0.1/++resource++zorgajax/prototype.js" type="text/javascript"></script>
            <script type="text/javascript">var livePageUUID = 'uuid2';</script>
            <script src="http://127.0.0.1/++resource++zorgajax/livepage.js" type="text/javascript"></script>
        </head>
        <body onload="startClient()">
        <p>Input some text.</p>
        <input onchange="sendEvent('append', 'target', this.value)" type="text" />
        <p id="target">Text goes here:</p>
        </body>
    </html>
   
The global utility can be asked for all online users:
        
    >>> manager.whoIsOnline(where)
    ['zorg.member.dominik', 'zorg.member.uwe']
    
For test purposes we set the refresh interval (i.e. the interval in which
output calls are renewed) to 0.1 seconds :
    
    >>> from zorg.live.page.client import LivePageClient
    >>> LivePageClient.refreshInterval = 0.1
  
After that the page can be called by the javascript glue as follows
    
    -  @@livepage.html/@@client/uuid0/output
    
       Call the output method and ask for special output that is intended
       for the specified client
   
    -  @@livepage.html/@@client/uuid0/input?verb=change&argument=42
        
       Call an input method that produces output for various clients.
      
After the startup we ask for some output. Since nothing happened, the
output is 'idle':
    
    >>> page1 = TestLivePage(None, TestRequest())
    >>> str(page1.output('uuid1'))
    'idle'
  
Now we can send some input. If we get the input from the browser we must first
be able to convert the text into a Python object. Since we can convert
url encoded arguments and post forms easily into dicts we decided to use
the global function ««dict2event«« as the basic factory.

This function uses named IClientEventFactory utilities to lookup the event 
from a verb that describes the event:

    >>> from zorg.live.page.event import dict2event
    >>> event = dict2event(dict(verb="append", id="id", html="<p>ABC</p>"))
    >>> event
    <zorg.live.page.event.Append object at ...>
    >>> str(event)
    'append id \n<p>ABC</p>'
    
The set of registered event types can be easily extended by registering a
new IClientEventFactory. Most of the time this will look as follows :

    >>> from zorg.live.page.interfaces import IClientEventFactory
    >>> class SpecialEvent(object) :
    ...     def __init__(self, **kw) :
    ...         self.__dict__.update(kw)

Note that the class must be provide the IClientEventFactory. We can achieve
this by using directlyProvides:

    >>> from zope.interface import directlyProvides
    >>> directlyProvides(SpecialEvent, IClientEventFactory)
    
    >>> dict2event(dict(verb='special', arg=42))
    Traceback (most recent call last):
    ...
    ComponentLookupError: (<InterfaceClass ...IClientEventFactory>, 'special')
    
After the registration of the class as a utility the conversion works:
    
    
    >>> zope.component.provideUtility(SpecialEvent, IClientEventFactory,
    ...                                                        name="special")
    >>> dict2event(dict(verb='special', arg=42))
    <SpecialEvent object at ...>
    
In Python contexts we can use the event classes directly :   
    
    >>> from zorg.live.page.event import Append
    >>> event1 = Append(id="target", html="<p>42</p>")
    
Now let's send the event to a LivePage :

    >>> page2 = TestLivePage(None, TestRequest()) 
    >>> page2.input('uuid1', event1)
    ''
    
After that the next call of the output returns javascript snippets:
        
    >>> print str(page1.output(uuid='uuid1'))
    append target
    <p>42</p>


And this again and again if we provide new input :
    
    >>> event2 = Append(id="target", html="<p>43</p>")
    >>> page2.input('uuid1', event2)
    ''
    
    >>> print str(page1.output('uuid1'))
    append target
    <p>43</p>
    


