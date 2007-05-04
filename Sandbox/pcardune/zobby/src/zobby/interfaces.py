from zope.interface import Interface, Attribute
from zope.app.container.interfaces import IContainer
from zope import schema

class IZobbyApplication(IContainer):
    """A Zobby Session."""

    users = Attribute("users")

    def addUser(self, username):
        """Connect a user to the app."""

    def removeUser(self, username):
        """Remove a user from the app."""

class ISession(IContainer):
    """A zobby session.... contains documents"""

    chatMessages = schema.List(
        title=u"chatMessages",
        required=True)

    title = schema.TextLine(
        title=u"Title",
        required=False)

    description = schema.TextLine(
        title=u"Short Description",
        required=False)

    def addChatMessage(message):
        """Add a message to the chat."""
