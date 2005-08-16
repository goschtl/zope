"""
Python code for z3checkins product.

Checkin message folder handling.

$Id: folder.py,v 1.5 2004/03/14 10:56:48 gintautasm Exp $
"""

from zope.interface import implements
from zope.app.container.btree import BTreeContainer
from zope.app.container.interfaces import INameChooser
from zope.app.container.interfaces import IContainerNamesContainer
from zope.app.size.interfaces import ISized
from interfaces import ICheckinFolder

class CheckinFolder(BTreeContainer):
    """A message folder."""

    implements(ICheckinFolder, IContainerNamesContainer)


class MessageNameChooser:
    """An adapter to choose names for messages."""

    implements(INameChooser)

    def __init__(self, context):
        pass

    def chooseName(self, name, message):
        return message.message_id

    def checkName(self, name, message):
        return name == message.message_id


class MessageSized:
    """An adapter to calculate size of a message."""
    implements(ISized)

    def __init__(self, message):
        self._message = message

    def sizeForSorting(self):
        return len(self._message.full_text)

    def sizeForDisplay(self):
        bytes = len(self._message.full_text)
        if bytes < 1024:
            return u'%d bytes' % bytes
        else:
            return u'%d KB' % (bytes / 1024)
