"""
Interfaces for the z3checkins product.

$Id$
"""

from zope.interface import Interface, Attribute
from zope.app.container.interfaces import IContainer, IContained
from zope.app.container.constraints import contains, containers
from zope.schema import Field, Text, TextLine, List, Object, Datetime


class IMessageUpload(Interface):
    pass


class IMessage(IMessageUpload):
    """Mail message."""

    message_id = TextLine(title=u"Unique message ID")
    author_name = TextLine(title=u"Author's real name")
    author_email = TextLine(title=u"Author's email address")
    subject = TextLine(title=u"Subject line of the message")
    date = Datetime(title=u"Date and time of the message")
    body = Text(title=u"Body of the message")
    full_text = Text(title=u"Full message text (headers and body)")


class ICheckinMessage(IMessage):
    """Checkin message."""

    directory = Attribute("Directory that was updated")
    branch = Attribute("Branch tag if this was commited to a branch")
    log_message = Attribute("Checkin log message")
    # Maybe added_files, modified_files, removed_files listing files and their
    # revisions


class IBookmark(Interface):
    """Bookmark placed between messages."""


class FormatError(Exception):
    """Ill-formed message exception"""


class IMessageParser(Interface):
    """Parser for RFC-822 checkin messages"""

    def parse(input):
        """Parses an RFC-822 format message from a 'input' (which can be a
        string or a file-like object) and returns an IMessage.

        If the message is a checkin message, returns an ICheckinMessage.

        May raise a FormatError if the message is ill-formed.
        """


class ICheckinFolderSchema(Interface):
    """Checkin folder properties"""

    description = TextLine(title=u"RSS view description",
                           required=False)
    archive_url = TextLine(title=u"URL of mailing list archive",
                           required=False)
    icons = Text(title=u"Icon definitions", required=False)


class ICheckinFolder(IContainer, ICheckinFolderSchema):
    """A marker interface for the checkins folder."""

    contains(IMessageUpload)

    messages = List(title=u"Messages",
                    description=u"""
                    Messages in this container, sorted by date in
                    descending order.
                    """,
                    value_type=Object(title=u"A message", schema=IMessage))


class IMessageContained(IContained):
    """A contained message."""

    containers(ICheckinFolder)
