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
from zope.interface import Interface
from zope.schema import Text, TextLine, Field

from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.interfaces import IContained, IContainer
from zope.app.file.interfaces import IFile


class IMessage(Interface):
    """A message object."""

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


class IMessageContained(IContained):
    """Interface that specifies the type of objects that can contain
    messages."""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(IMessageBoard, IMessage))


class IMessageContainer(IContainer):
    """We also want to make the message object a container that can contain
    responses (other messages) and attachments (files and images)."""

    def __setitem__(name, object):
        """Add a IMessage object."""

    __setitem__.precondition = ItemTypePrecondition(IMessage, IFile)
