##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Message Implementation

An implementation of the Message using BTreeContainers as base.

$Id: message.py,v 1.1 2003/06/07 11:24:48 srichter Exp $
"""
from zope.interface import implements
from zope.app.container.btree import BTreeContainer
from zope.app.size.interfaces import ISized

from book.messageboard.interfaces import IMessage
from book.messageboard.interfaces import IMessageContained, IMessageContainer

class Message(BTreeContainer):
    """A simple implementation of a message.

    Make sure that the ``Message`` implements the ``IMessage`` interface:

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IMessage, Message)
    True

    Here is an example of changing the title and description of the message:

    >>> message = Message()
    >>> message.title
    u''
    >>> message.body
    u''
    >>> message.title = u'Message Title'
    >>> message.body = u'Message Body'
    >>> message.title
    u'Message Title'
    >>> message.body
    u'Message Body'
    """
    implements(IMessage, IMessageContained, IMessageContainer)

    # See book.messageboard.interfaces.IMessage
    title = u''

    # See book.messageboard.interfaces.IMessage
    body = u''

  
class MessageSized(object):

    implements(ISized)
    __used_for__ = IMessage

    def __init__(self, message):
        self._message = message

    def sizeForSorting(self):
        """See ISized

        Create the adapter first.

        >>> size = MessageSized(Message())

        Here are some examples of the expected output.

        >>> size.sizeForSorting()
        ('item', 0)
        >>> size._message['msg1'] = Message()
        >>> size.sizeForSorting()
        ('item', 1)
        >>> size._message['att1'] = object()
        >>> size.sizeForSorting()
        ('item', 2)
        """
        return ('item', len(self._message))

    def sizeForDisplay(self):
        """See ISized

        Create the adapter first.

        >>> size = MessageSized(Message())

        Here are some examples of the expected output.

        >>> size.sizeForDisplay()
        u'0 replies, 0 attachments'
        >>> size._message['msg1'] = Message()
        >>> size.sizeForDisplay()
        u'1 reply, 0 attachments'
        >>> size._message['msg2'] =  Message()
        >>> size.sizeForDisplay()
        u'2 replies, 0 attachments'
        >>> size._message['att1'] = object()
        >>> size.sizeForDisplay()
        u'2 replies, 1 attachment'
        >>> size._message['att2'] = object()
        >>> size.sizeForDisplay()
        u'2 replies, 2 attachments'
        """
        messages = 0
        for obj in self._message.values():
            if IMessage.providedBy(obj):
                messages += 1

        attachments = len(self._message)-messages

        if messages == 1: size = u'1 reply'
        else: size = u'%i replies' %messages

        if attachments == 1: size += u', 1 attachment'
        else: size += u', %i attachments' %attachments

        return size
