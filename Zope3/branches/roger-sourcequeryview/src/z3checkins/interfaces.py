"""
Interfaces for the z3checkins product.

$Id: interfaces.py,v 1.14 2004/05/15 13:23:57 gintautasm Exp $
"""

from zope.interface import Interface, Attribute
from zope.app.folder.interfaces import IFolder
from zope.app.container.interfaces import IContainer, IContained
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.schema import Field, Text, TextLine


class IMessageUpload(Interface):
    pass


class IMessage(IMessageUpload):
    """Mail message."""

    message_id = Attribute("Unique message ID")
    author_name = Attribute("Author's real name")
    author_email = Attribute("Author's email address")
    subject = Attribute("Subject line of the message")
    date = Attribute("Date and time of the message")
    body = Attribute("Body of the message")
    full_text = Attribute("Full message text (headers and body)")


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


class ICheckinFolder(IFolder, ICheckinFolderSchema):
    """A marker interface for the checkins folder."""

    def __setitem__(name, object):
        """Add a message"""

    __setitem__.precondition = ItemTypePrecondition(IMessageUpload)


class IMessageContained(IContained):
    """A contained message."""

    __parent__ = Field(constraint=ContainerTypesConstraint(ICheckinFolder))


class IMessageArchive(Interface):
    """A chronologically ordered sequence of messages.

    Implements the Python sequence procotol.
    """

    def __len__():
        """Returns the number of messages in the archive."""

    def __getitem__(index):
        """Returns a given message."""

    def __getslice__(start, stop):
        """Returns a range of messages."""

    def __iter__():
        """Returns an iterator."""

    def index(message):
        """Returns the index of a given message.

        Raises ValueError if message is not in the archive.
        """

