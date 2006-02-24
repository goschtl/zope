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

import zope, transaction
from datetime import datetime
import pytz

from zope.interface import implements
from zope.component import adapts
from zope.app import zapi
from zope.publisher.browser import TestRequest
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView
from zope.app.dublincore.interfaces import IZopeDublinCore

from zope.app.event.interfaces import IObjectModifiedEvent

from zorg.edition.interfaces import IUUIDGenerator
from zorg.comment import IComments
from zorg.comment import ICommentSequence

from zorg.live.page.client import LivePageClient
from zorg.live.page.page import LivePage
from zorg.live.page.event import Append
from zorg.live.page.event import Update
from zorg.live.page.interfaces import ILivePageManager
from zorg.live.page.interfaces import IPersonEvent

from zorg.live.globals import getRequest
from zorg.live.globals import getFullName

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
    '1'
    >>> LiveComments(file, TestRequest()).addComment("Another comment")
    '2'
    
    >>> page = LiveComments(file, TestRequest())
    >>> print page.renderComments()
    <div id="comments">...
    ...<p>A comment</p>...
    ...<p>Another comment</p>...
    ...
    
   
    
    """

    _comment = ViewPageTemplateFile("./templates/comment.pt")
     
    clientFactory = LiveCommentsClient
    
    def __init__(self, context, request) :
        super(LiveComments, self).__init__(context, request)
        self.comments = IComments(self.context)
        self.formatter = request.locale.dates.getFormatter('dateTime', 'medium')
        
    def format(self, datetime) :
        try :
            return self.formatter.format(datetime)
        except :
            return str(datetime)
    
    def addComment(self, text) :
        """ Starts a live comment. Saves a first nearly empty version
            and returns the new key.
        """
        comments = IComments(self.context)
        return str(comments.addComment(text))
        
    def saveComment(self, key, text) :
        """ Saves the last text of the live comment. """
        comments = IComments(self.context)
        comments.editComment(key, text)
        return "saved"
        
    def cancelComment(self, key) :
        """ Cancels the edit session and deletes the persistent comment. """
        comments = IComments(self.context)
        del comments[key]
        return "canceled"
        
    def whoIsOnline(self) :
        """ Returns a comma seperated list of names of online users. """
        manager = zapi.getUtility(ILivePageManager)
        ids = manager.whoIsOnline(self.getLocationId())
        return ", ".join([getFullName(id) for id in ids])
      
        
    def renderComment(self, key, comment, livetext=None) :
    
        if livetext is not None :
            text = livetext
        else :
            text = unicode(comment.data, encoding="utf-8")
            
        info = self.info = dict()
        dc = IZopeDublinCore(comment)
        info['live'] = False
        info['comment_id'] = "comment%s" % key
        info['text_id'] = "text%s" % key
        info['key'] = key
        info['who'] = ", ".join(getFullName(x) for x in dc.creators)
        info['when'] = self.format(dc.created)
        info['text'] = self.makeParagraph(text)
        return self._comment()
 
 
    def renderComments(self) :
    
        result = ['<div id="comments">']
        
        comments = self.comments
        for key, value in comments.items() :
            result.append(self.renderComment(key, value))
        result.append('</div>')
        
        return "".join(result)

                
    def makeParagraph(cls, text) :
        text = text.replace("\n", "<br/>")
        return "<p>%s</p>" % text

    makeParagraph = classmethod(makeParagraph)

        
    def notify(cls, event) :

        if IPersonEvent.providedBy(event) :
            manager = zapi.getUtility(ILivePageManager)
            repr = manager.whoIsOnline(event.where)
            update = Update(id="online", html=repr)
            cls.sendEvent(update)
        
        if IObjectModifiedEvent.providedBy(event) :
            t = transaction.get()
            for desc in event.descriptions :

                if ICommentSequence.providedBy(desc) :
                    if IComments == desc.interface :
                        method = cls.onCommentModified
                        # XXX Replace with addAfterCommitHook in ZODB 3.7
                        t.addBeforeCommitHook(method, (event, desc))
                                                
                        
            
    notify = classmethod(notify)

            
    def onCommentModified(cls, event, desc) :
        """ Event handler for new comments. Note that this event handler
            responds to Zopes ObjectModifiedEvent that reflects a change
            in the ZODB.
        """
        
        context = event.object
        comments = IComments(context)
        page = LiveComments(context, getRequest())             
        key = desc.keys[0]

        if desc.change == "add" :
            persistent = comments[key]
            r = page.renderComment(key, persistent).encode('utf-8')
            event = Append(id="comments", html=r, extra="scroll")    
        elif desc.change == "del" :
            r = page.renderComments().encode('utf-8')
            event = Update(id="comments", html=r) 
        else :
            persistent = comments[key]
            text = cls.makeParagraph(persistent.data)
            event = Update(id="text%s" % key, html=text)    
            
        cls.sendEvent(event)
        
    onCommentModified = classmethod(onCommentModified)
    

