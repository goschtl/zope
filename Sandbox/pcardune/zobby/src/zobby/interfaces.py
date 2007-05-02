from zope.interface import Interface, Attribute
from zope.app.container.interfaces import IContainer


class IZobbyApplication(IContainer):
    """A Zobby Session."""

    users = Attribute("users")

    def addUser(self, username):
        """Connect a user to the app."""

    def removeUser(self, username):
        """Remove a user from the app."""

class ISession(IContainer):
    """A zobby session.... contains documents"""

    chatMessages = Attribute("chat messages")

    def addChatMessage(message):
        """Add a message to the chat."""
