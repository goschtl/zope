====
Live
====

This package is experimental. It contains a LivePage implementation that
is similar to and inspired by Nevows LivePages, see also 

    http://divmod.org/trac/wiki/DivmodNevow
  
Installation
------------

The current implementation runs to a limited degree with Zope3's buildin
servers. To enable LivePage for more users than server threads
you must install the LiveServer that is included in this package. Add the
following lines to your 'zope.conf' file :

    <server>
      type LiveServerHTTP
      address 8088
    </server>



Basic idea
----------

LivePages try to overcome the traditional model of web pages in which the
content of the page is refreshed in response to a user activity. Besides the
typically request response cycle that is under the control of the user
a LivePage opens a background request that waits for notification of server
side messages. This background request hangs until a notification arives,
performs some page updating or other javascripts upon notification, and
repeats a new request for further notifications. This means 
that each LivePage constantly opens HTTP channels, waits until a notification
arrives (which might be an idle one), closes the channel and immediately
reopens a new channel. Since many notifications are broadcasted to several
users this might lead to massive concurrent requests, which start nearly
at the same time.


Main problem
------------

Zope is not well-suited for this performance model since each request is handled
in a seperate thread with its own database connections and object cache. 
For most of the background requests for notification this is an unnecessary 
overhead that limits the number of connected users to the number of available 
threads. This might work for two or three users but not for 20 users or more 
which are concurrently online and share the same resources.

Therefore this package contains a specialization of Zope3's twisted server
that handles all LivePage requests that do not need database connections  
outside of the ordinary Zope3 threads. The Zope3 requests still work of course
but should be restricted to security or persistence issues as far as possible.


Usage
-----

LivePages are special BrowserViews that install a LivePageClient on the server
side for each page that is connected to LivePage server. The LivePageClient
is registered in a central utility, which provides access across requests
to the same global datastructures which can be accessed in a thread safe way.

    >>> from zorg.live.page.manager import LivePageManager
    >>> from zorg.live.page.interfaces import ILivePageManager
    >>> manager = LivePageManager()
    >>> zope.component.provideUtility(manager, ILivePageManager)

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
        <input onchange="sendLivePage('append', 'target', this.value)" type="text" />
        <p id="target">Text goes here:</p>
        </body>
    </html>
   
The global utility can be asked for all online users:
        
    >>> manager.whoIsOnline(group_id)
    ['zorg.member.dominik', 'zorg.member.uwe']
    
For test purposes we set the refresh interval (i.e. the interval in which
output calls are renewed) to 0.1 seconds :
    
    >>> from zorg.live.page.client import LivePageClient
    >>> LivePageClient.refreshInterval = 0.1
  
After that the page can be called by the javascript glue as follows
    
    -  @@livepage.html/@@client/uuid0/output?outputNum=0
    
       Call the output method and ask for special output that is intended
       for the specified client
   
    -  @@livepage.html/@@client/uuid0/input?handler-name=change&arguments=42
        
       Call an input method that produces output for various clients.
      
After the startup we ask for some output. Since nothing happened, the
output is 'idle':
    
    >>> page1 = TestLivePage(None, TestRequest())
    >>> page1.output(uuid='uuid1', outputNum=0)
    'idle'
  
Now we can send some input :
    
    >>> page2 = TestLivePage(None, TestRequest())
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
    


