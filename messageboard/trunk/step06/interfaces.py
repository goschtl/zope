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
from zope.i18n import MessageIDFactory
from zope.interface import Interface
from zope.interface import classImplements
from zope.schema import Text, TextLine, Field, Tuple
from zope.schema.interfaces import IText

from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.interfaces import IContained, IContainer
from zope.app.file.interfaces import IFile

from fields import HTML

_ = MessageIDFactory('messageboard')


class IMessage(Interface):
    """A message object."""

    title = TextLine(
        title=_("Title/Subject"),
        description=_("Title and/or subject of the message."),
        default=u"",
        required=True)

    body = HTML(
        title=_("Message Body"),
        description=_("This is the actual message. Type whatever!"),
        default=u"",
        allowed_tags=('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'a',
                      'br', 'b', 'i', 'u', 'em', 'sub', 'sup',
                      'table', 'tr', 'td', 'th', 'code', 'pre',
                      'center', 'div', 'span', 'p', 'font', 'ol',
                      'ul', 'li', 'q', 's', 'strong'),
        required=False)


class IMessageBoard(IContainer):
    """The message board is the base object for our package. It can only
    contain IMessage objects."""

    def __setitem__(name, object):
        """Add a IMessage object."""

    __setitem__.precondition = ItemTypePrecondition(IMessage)

    description = Text(
        title=_("Description"),
        description=_("A detailed description of the content of the board."),
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


class IHTML(IText):
    """A text field that handles HTML input."""

    allowed_tags = Tuple(
        title=_("Allowed HTML Tags"),
        description=_("""\
        Only listed tags can be used in the value of the field.
        """),
        required=False)

    forbidden_tags = Tuple(
        title=_("Forbidden HTML Tags"),
        description=_("""\
        Listed tags cannot be used in the value of the field.
        """),
        required=False)

classImplements(HTML, IHTML)
