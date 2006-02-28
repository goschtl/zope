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
        
        
        XXX: has to be rewritten since LivePages are now in zorg.live
       
    """
    
    _comments = ViewPageTemplateFile("./templates/comments.pt")
    
    def __init__(self, context, request) :
        super(LiveComments, self).__init__(context, request)
        self.comments = CommentsList(self)
    
    def online(self) :
        global clients
        members = set()
        for client in clients :
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
        
