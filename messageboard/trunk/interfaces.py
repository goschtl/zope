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
"""Message Board Interfaces

Interfaces for the Zope 3 based Message Board Package 

$Id$
"""
from zope.schema import Text, TextLine, Field

from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.interfaces import IContainer


class IMessage(IContainer):
    """A message object. It can contain its own responses."""

    title = TextLine(
        title=u"Title/Subject",
        description=u"Title and/or subject of the message.",
        default=u"",
        required=True)

    body = Text(
        title=u"Message Body",
        description=u"This is the actual message. Type whatever you wish.",
        default=u"",
        required=False)


class IMessageBoard(IContainer):
    """The message board is the base object for our package. It can only
    contain IMessage objects."""

    def __setitem__(name, object):
        """Add a IMessage object."""

    __setitem__.precondition = ItemTypePrecondition(IMessage)

    description = Text(
        title=u"Description",
        description=u"A detailed description of the content of the board.",
        default=u"",
        required=False)


IMessage['__setitem__'].setTaggedValue('precondition',
                                       ItemTypePrecondition(IMessage))
IMessage.setTaggedValue('__parent__', Field(
    constraint=ContainerTypesConstraint(IMessageBoard, IMessage)))
