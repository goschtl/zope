"""
Python code for z3checkins product.

Checkin message folder handling.

$Id$
"""

from persistent.list import PersistentList
from zope.interface import implements
from zope.app.container.btree import BTreeContainer
from zope.app.container.interfaces import INameChooser
from zope.app.container.interfaces import IContainerNamesContainer
from zope.app.size.interfaces import ISized
from z3checkins.interfaces import ICheckinFolder, IMessage


class CheckinFolder(BTreeContainer):
    """A message folder.

    The attribute `messages` is a list of Messages sorted by date in
    reverse order (that is, latest messages first).  It was introduced for
    performance reasons.
    """

    implements(ICheckinFolder, IContainerNamesContainer)

    description = None
    archive_url = None
    icons = None

    def __init__(self):
        BTreeContainer.__init__(self)
        self.messages = PersistentList()

    def __setitem__(self, key, message):
        BTreeContainer.__setitem__(self, key, message)
        if IMessage.providedBy(message):
            for ind, oldmsg in enumerate(self.messages):
                if message.date > oldmsg.date:
                    self.messages.insert(ind, message)
                    break
            else:
                self.messages.append(message)

    def __delitem__(self, key):
        message = self.get(key)
        if IMessage.providedBy(message):
            for ind, oldmsg in enumerate(self.messages):
                if oldmsg is message:
                    self.messages.pop(ind)
                    break
        BTreeContainer.__delitem__(self, key)

    def __setstate__(self, state):
        """Rebuild the internal message date index.

        This method is for backwards compatibility, so that data does
        not need to be reimported into existing z3checkins instances.
        """
        # BBB 2005-01-05
        BTreeContainer.__setstate__(self, state)
        if not hasattr(self, 'messages'):
            self.messages = [msg for msg in self.values()
                             if IMessage.providedBy(msg)]
            self.messages.sort(lambda msg1, msg2: cmp(msg2.date, msg1.date))
        if not isinstance(self.messages, PersistentList):
            self.messages = PersistentList(self.messages)


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
