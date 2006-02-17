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

import zope, datetime

from zope.interface import implements
from zope.component import adapts
from zope.component import ComponentLookupError
from zope.app import zapi
from zope.publisher.browser import TestRequest
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.security.interfaces import PrincipalLookupError

from zorg.comment import IComments

from zorg.live.page.client import LivePageClient
from zorg.live.page.page import LivePage
from zorg.edition.interfaces import IUUIDGenerator

def getFullName(principal_id) :
    """ Returns the full name or title of a principal that can be used
        for better display.
        
        Returns the id if the full name cannot be found.
    """
    try :
        return zapi.principals().getPrincipal(principal_id).title
    except (PrincipalLookupError, AttributeError, ComponentLookupError) :
        return principal_id
        

class LiveCommentsClient(LivePageClient) :
    """ A specialization that holds infos about 
        pending comments, i.e. comments that are typed by the user
        but not save to the ZODB.
    """
    
    def __init__(self, page, uuid=None) :
        super(LiveCommentsClient, self).__init__(page, uuid)
        self.pending = {}       # a dict of sender, value items


class LiveComments(LivePage) :
    """ A simple live view for comments. Allows the user to immediately
        see how he/she and others type comments.
    
    >>> from zorg.comment.browser.tests import buildTestFile
    >>> file = buildTestFile()
   
    >>> page = LiveComments(file, TestRequest())
    >>> print page.renderComments()
    <div id="comments"></div>
    
    
    
    We can also add the texts as persistent comments:
    
    >>> LiveComments(file, TestRequest()).addComment("A comment")
    >>> LiveComments(file, TestRequest()).addComment("Another comment")
    
    >>> page = LiveComments(file, TestRequest())
    >>> print page.renderComments()
    <div id="comments"><a name="comment1"></a>
    ...
    <div id="comment1">A comment</div>
    ...
    <a name="comment2"></a>
    ...
    <div id="comment2">Another comment</div>
    ...
    
   
    
    """

    _comment = ViewPageTemplateFile("./templates/comment.pt")
     
    clientFactory = LiveCommentsClient
    
    def __init__(self, context, request) :
        super(LiveComments, self).__init__(context, request)
        self.comments = IComments(self.context)
        
    def startComment(self, comment) :
        group_id = self.getGroupId()
        uuid = zapi.getUtility(IUUIDGenerator)()
        r = self.renderPendingComment(comment, uuid).encode('utf-8')
        response = 'append comments\n%s\n' % (r)
        
        self.sendResponse(response, group_id)
        return uuid
   
    def renderPendingComment(self, text, uuid) :
        who = self.request.principal.id
        info = self.info = dict()
        info['id'] = uuid
        info['key'] = uuid
        info['who'] = getFullName(who)
        info['when'] = datetime.datetime.utcnow() 
        info['text'] = text
        return self._comment()
        
    def renderComments(self) :
    
        result = ['<div id="comments">']
        
        comments = self.comments
        for key, value in comments.items() :
            info = self.info = dict()
            dc = IZopeDublinCore(value)
            info['id'] = "comment%s" % key
            info['key'] = key
            info['who'] = ", ".join(getFullName(x) for x in dc.creators)
            info['when'] = dc.created
            info['text'] = unicode(value.data, encoding="utf-8")
            
            result.append(self._comment())
        
        result.append('</div>')
        
        return "".join(result)
                
    def addComment(self, text) :
        comments = IComments(self.context)
        comments.addComment(text)
        
    
    
    
    
