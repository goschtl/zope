##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Skin for the message board

$Id$
"""
import random, time, cgi

from zope.interface import implements
from zope.app import zapi
from zope.app.dublincore.interfaces import ICMFDublinCore
from zope.app.form.interfaces import IInputWidget
from zope.app.form.utility import setUpWidgets
from zope.app.workflow.interfaces import IProcessInstanceContainer

from book.messageboard.interfaces import IMessage
from book.messageboard.browser.messageboard import hasMessageStatus
from book.messageboard.browser.messageboard import ReviewMessages
from book.messageboard.browser.thread import Thread

class Posts(object):

    def getPosts(self):
        """Get first level post infos as ZPT-friendly dict."""
        posts = []
        for name, post in self.context.items():
            if hasMessageStatus(post, 'published'):
                dc = ICMFDublinCore(post)
                info = {}
                info['title'] = post.title
                if len(post.body) > 100:
                    body = post.body[:100] + '...'
                else:
                    body = post.body
                info['body'] = body
                
                replies = 0
                for obj in post.values():
                    if IMessage.providedBy(obj):
                        replies += 1
                info['replies'] = replies
                
                info['creator'] = dc.creators[0]
                formatter = self.request.locale.dates.getFormatter(
                    'dateTime', 'short')
                info['created'] = formatter.format(dc.created)
                info['url'] = './' + name + '/@@details.html'
                posts.append(info)
        return posts
  
class AddMessage(object):
    """Add-Form supporting class."""

    def nextURL(self):
        return '../@@posts.html'

    def namesAccepted(self):
        return False

  
class Review(ReviewMessages):
    """Review messages for publication."""
    
    def getPendingMessagesInfo(self):
        """Get all the display info for pending messages"""
        msg_infos = []
        for msg in self.getPendingMessages(self.context):
            dc = ICMFDublinCore(msg)
            info = {}
            info['path'] = zapi.getPath(msg)
            info['title'] = msg.title
            info['creator'] = dc.creators[0]
            formatter = self.request.locale.dates.getFormatter(
                'dateTime', 'medium')
            info['created'] = formatter.format(dc.created)
            info['url'] = zapi.getView(
                msg, 'absolute_url', self.request)() + \
                '/@@details.html'
            msg_infos.append(info)
        return msg_infos
  
    def updateStatus(self, messages):
        """Upgrade the stati from 'pending' to 'published'."""
        if not isinstance(messages, (list, tuple)):
            messages = [messages]
            
        for path in messages:
            msg = zapi.traverse(self.context, path)
  
            adapter = IProcessInstanceContainer(msg)
            adapter['publish-message'].fireTransition('pending_published')
  
        return self.request.response.redirect('@@review.html')

class Details(Thread, object):
    """Message Details view class."""

    def metadata(self):
        """Get the relevant metadata from the message."""
        dc = ICMFDublinCore(self.context)
        info = {}
        info['creator'] = dc.creators[0]
        formatter = self.request.locale.dates.getFormatter('dateTime', 'medium')
        info['created'] = formatter.format(dc.created)
        return info

    def htmlBody(self):
        """Make the body HTML-savy."""
        body = cgi.escape(self.context.body)
        return body.replace('\n', '<br/>\n')

    def getParentURL(self):
        """Get the best view URL for the parent.

        Since messages can be contained by message boards and messages, we
        have different URLs based on the parent type.
        """
        parent = zapi.getParent(self.context)
        if IMessage.providedBy(parent):
            return '../@@details.html'
        else:
            return '../@@posts.html'

    def listContentInfo(self):
        """Override the thread listContentInfo() to get an appropriate URL."""
        info = super(Details, self).listContentInfo()
        for item in info:
            item['url'] = item['url'].replace('@@thread.html', '@@details.html')
        return info


class ReplyMessage:
    """Add-Form supporting class."""
  
    def nextURL(self):
        return '../@@details.html'
  
    def _setUpWidgets(self):
        """Alllow addforms to also have default values."""
        parent = self.context.context
        title = parent.title
        if not title.startswith('Re:'):
            title = 'Re: ' + parent.title
  
        dc = ICMFDublinCore(parent)
        formatter = self.request.locale.dates.getFormatter(
              'dateTime', 'medium')
        body = '%s on %s wrote:\n' %(dc.creators[0], 
                                    formatter.format(dc.created))
        body += '> ' + parent.body.replace('\n', '\n> ')
          
        setUpWidgets(self, self.schema, IInputWidget, 
                     initial={'title': title, 'body': body},
                     names=self.fieldNames)
