import zope.interface
import zope.schema

class IChatRoom(zope.interface.Interface):
    """A simple chat room."""

    messages = zope.schema.List(
        title=u"Messages",
        description=u"The Chat Messages.",
        readonly=True,
        required=True)

    topic = zope.schema.TextLine(
        title=u"Topic",
        description=u"Topic of the Chat Room.",
        required=True)

    def addMessage(message):
        """Add a message to the list."""
