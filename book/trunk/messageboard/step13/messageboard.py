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
"""Message Board Implementation

An implementation of the Message Board using BTreeContainers as base.

$Id$
"""
from zope.interface import implements
from zope.app.annotation.interfaces import IAnnotations
from zope.app.container.btree import BTreeContainer

from book.messageboard.interfaces import IMessageBoard
from book.messageboard.interfaces import IPlainText, ISmileyThemeSpecification

ThemeKey = 'http://www.zope.org/messageboard#1.0/SmileyTheme'

class MessageBoard(BTreeContainer):
    """A very simple implementation of a message board using B-Tree Containers

    Make sure that the ``MessageBoard`` implements the ``IMessageBoard``
    interface:

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IMessageBoard, MessageBoard)
    True
    
    Here is an example of changing the description of the board:

    >>> board = MessageBoard()
    >>> board.description
    u''
    >>> board.description = u'Message Board Description'
    >>> board.description
    u'Message Board Description'
    """
    implements(IMessageBoard)

    # See book.messageboard.interfaces.IMessageBoard
    description = u''


class PlainText:

    implements(IPlainText)

    def __init__(self, context):
        self.context = context

    def getText(self):
        return self.context.description

    def setText(self, text):
        self.context.description = unicode(text)


class SmileyThemeSpecification(object):

    implements(ISmileyThemeSpecification)
    __used_for__ = IMessageBoard

    def __init__(self, context):
        self.context = context
        self._annotations = IAnnotations(context)
        if self._annotations.get(ThemeKey, None) is None:
            self._annotations[ThemeKey] = 'default'

    def getTheme(self):
        return self._annotations[ThemeKey]

    def setTheme(self, value):
        self._annotations[ThemeKey] = value
        
    # See .interfaces.ISmileyThemeSpecification
    theme = property(getTheme, setTheme)
