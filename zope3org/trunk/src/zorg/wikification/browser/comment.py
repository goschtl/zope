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

$Id: comment.py 38895 2005-10-07 15:09:36Z dominikhuber $
"""
__docformat__ = 'restructuredtext'

import zope

from zope.interface import implements
from zope.component import adapts
from zope.app import zapi
from zope.publisher.browser import TestRequest
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView
from zope.app.dublincore.interfaces import IZopeDublinCore

from zope.app.event.interfaces import IObjectModifiedEvent
from zope.app.event.interfaces import ISequence


from zorg.comment import IComments
from zorg.comment.browser.comment import getFullName

from zorg.ajax.page import PageElement
from zorg.ajax.interfaces import IAjaxUpdateable
from zorg.ajax.livepage import LivePage
from zorg.ajax.livepage import LivePageClient
from zorg.ajax.livepage import clients

from zorg.wikification.browser.wikipage import WikiPage
        
class CommentsList(PageElement) :
    """ A simple list view for comments. 
    """

    implements(IAjaxUpdateable)
    
    _comment = ViewPageTemplateFile("./templates/comment.pt")
        
    def __init__(self, page) :
        super(CommentsList, self).__init__(page)
        self.comments = IComments(self.context)
        
    def render(self, method=None, parameter=None) :
    
        result = ['<div id="comments">']
        
        comments = self.comments
        for key, value in comments.items() :
            info = self.info = dict()
            dc = IZopeDublinCore(value)
            info['key'] = key
            info['who'] = ", ".join(getFullName(x) for x in dc.creators)
            info['when'] = dc.created
            info['text'] = unicode(value.data, encoding="utf-8")
            
            result.append(self._comment())
        
        result.append('</div>')
        
        return "".join(result)
        
        
class LiveComments(WikiPage, LivePage) :
    """ A view that shows all added comments 'live', i.e. the view
        is updated in all browsers as soon as the server side
        list of comments changes.
        
        As an example we use a discussion about single file:
        
        >>> from zorg.comment.browser.tests import buildTestFile
        >>> file = buildTestFile()
        >>> import zope.event
        >>> from zorg.ajax.livepage import livePageSubscriber
        >>> zope.event.subscribers.append(livePageSubscriber) 
        
        >>> class Principal(object) :
        ...     def __init__(self, id, title) :
        ...         self.id = id
        ...         self.title = title
        
        >>> user1 = Principal('zorg.member.uwe', u'Uwe Oestmeier')
        >>> user2 = Principal('zorg.member.dominik', u'Dominik Huber')
        
        >>> class SampleLiveComments(LiveComments) :
        ...     def render(self) :
        ...         return '<html>client %s</html>' % self.nextClientId()
        
        >>> request = TestRequest()
        >>> request.setPrincipal(user1)
        >>> page1 = SampleLiveComments(file, request)
        >>> page1.render()
        '<html>client 0</html>'
        >>> client1 = clients['0']
        
        >>> request = TestRequest()
        >>> request.setPrincipal(user2)
        >>> page2 = SampleLiveComments(file, request)
        >>> page2.render()
        '<html>client 1</html>'
        >>> client2 = clients['1']
        
        For test purposes we set the refresh interval (i.e. the interval in which
        output calls are renewed) to 0.1 seconds :
        
        >>> for client in clients.values() : 
        ...     client.refreshInterval = 0.1
    
        Both users can see that they are online :
        
        >>> page1.online()
        [u'Dominik Huber', u'Uwe Oestmeier']
        
        If one of them adds a comment the other client is immediately informed:
        
        >>> AddComment(file, TestRequest()).addComment("My comments")
        >>> print page1.output(0, 0)
        update comments
        <a name="comment1"></a>
        ...
        
        >>> print page2.output(1, 0)
        update comments
        <a name="comment1"></a>
        ...
       
    """
    
    _comments = ViewPageTemplateFile("./templates/comments.pt")
    
    def __init__(self, context, request) :
        super(LiveComments, self).__init__(context, request)
        self.comments = CommentsList(self)
    
    def online(self) :
        global clients
        members = set()
        for client in clients.values() :
            members.add(client.principal.title)
        return sorted(members)
                                    
    def notify(cls, event) :
        if IObjectModifiedEvent.providedBy(event) :
            for desc in event.descriptions :
                if ISequence.providedBy(desc) :
                    if IComments == desc.interface :
                        page = LiveComments(event.object, TestRequest())
                        html = page.innerPart("comments")
                        response = 'update comments\n%s' % (html)
                        cls.sendResponse(response)

    notify = classmethod(notify)
    
    def render(self) :
        return self._comments()
        



class AddComment(WikiPage) :
    """ A simple add view for comments. Allows the user to type comments
        and submit them.
        
    """
    
    def __init__(self, context, request) :
        super(AddComment, self).__init__(context, request)
        self.title = u"Add Comment"
        
    def nextURL(self) :
        url = zapi.absoluteURL(self.context, self.request)
        return url + "/@@wikiaddcomment.html"
         
    def addComment(self, text) :
        comments = IComments(self.context)
        comments.addComment(text)
        
        self.request.response.redirect(self.nextURL())
        
