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

from book.messageboard.interfaces import IMessage

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
    implements(IMessage)

    # See book.messageboard.interfaces.IMessage
    title = u''

    # See book.messageboard.interfaces.IMessage
    body = u''
