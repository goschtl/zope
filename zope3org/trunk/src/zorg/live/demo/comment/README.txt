LiveComments Demo
=================

This demo shows how several users can observe live how they type their comments.
The comment text is broadcasted every second or so to all clients that share 
the comment page and thus give the impression of immediate group awareness.

    >>> from zorg.live.page.manager import LivePageManager
    >>> from zorg.live.page.interfaces import ILivePageManager
    >>> manager = LivePageManager()
    >>> zope.component.provideUtility(manager, ILivePageManager)

For test purposes we set the refresh interval (i.e. the interval in which
output calls are renewed) to 0.1 seconds :
    
    >>> from zorg.live.page.client import LivePageClient
    >>> LivePageClient.refreshInterval = 0.1

Now we simulate the startup of two clients. We need a shared file in order
to attach comments to the file:

    >>> from zorg.live.demo.comment.tests import buildTestFile
    >>> file = buildTestFile()

    >>> from zorg.live.demo.comment.comment import LiveComments
    
    >>> class Principal(object) :
    ...     def __init__(self, id, title) :
    ...         self.id = id
    ...         self.title = title
    
    >>> user1 = Principal('zorg.member.uwe', u'Uwe Oestmeier')
    >>> user2 = Principal('zorg.member.dominik', u'Dominik Huber')

Note that the startup is simulated by the nextClientId() call :

    >>> request = TestRequest()
    >>> request.setPrincipal(user1)
    >>> page1 = LiveComments(file, request)
    >>> page1.nextClientId()
    'uuid1'
    >>> where1 = page1.getLocationId()
    
    >>> request.setPrincipal(user2)
    >>> page2 = LiveComments(file, request)
    >>> page2.nextClientId()
    'uuid2'
    >>> where2 = page2.getLocationId()
    
Both users share the same group resp. context :
    
    >>> where1 == where2
    True
   
We ask the global utility to ensure that both users are online:
        
    >>> manager.whoIsOnline(where1)
    ['zorg.member.dominik', 'zorg.member.uwe']
    
When the user starts typing, the Ajax textarea observer calls startComment which
broadcasts a new pending comment div that can be appended to the DOM children
of the 'comments' element of each browser client. 

The startComment call returns a uuid that can be used to update the text of the
new DOM element later on :

    >>> page1.startComment("Abc")
    'uuid3'

    >>> out1 = page1.output('uuid1')
    >>> print out1
    append comments scroll
    ...
    <div id="uuid3">Abc</div>
    ...
 
    >>> out1 == page2.output('uuid2')
    True

After that the client of the first user sends updates for the text element
with the new uuid.

