##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""XML-RPC Representations

$Id$
"""
from zope.event import notify
from zope.app.publisher.xmlrpc import MethodPublisher

from zope.app.event.objectevent import ObjectCreatedEvent, ObjectModifiedEvent

from book.messageboard.message import Message


class MessageContainerMethods(MethodPublisher):

  def getMessageNames(self):
      """Get a list of all messages."""
      return list(self.context.keys())

  def addMessage(self, name, title, body):
      """Add a message."""
      msg = Message()
      msg.title = title
      msg.body = body
      notify(ObjectCreatedEvent(msg))
      self.context[name] = msg
      return name

  def deleteMessage(self, name):
      """Delete a message. Return True, if successful."""
      self.context.__delitem__(name)
      return True 


class MessageMethods(MessageContainerMethods):

    def getTitle(self):
        return self.context.title

    def setTitle(self, title):
        self.context.title = title
        notify(ObjectModifiedEvent(self.context))
        return True

    def getBody(self):
        return self.context.body

    def setBody(self, body):
        self.context.body = body
        notify(ObjectModifiedEvent(self.context))
        return True


class MessageBoardMethods(MessageContainerMethods):

    def getDescription(self):
        return self.context.description

    def setDescription(self, description):
        self.context.description = description
        notify(ObjectModifiedEvent(self.context))
        return True
