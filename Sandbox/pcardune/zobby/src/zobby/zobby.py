from persistent import Persistent
from persistent.list import PersistentList
from zope.interface import implements
from zope.app.container import btree

import interfaces


class ZobbyApplication(btree.BTreeContainer):
    """The Zobby Application object"""
    implements(interfaces.IZobbyApplication)

    def __init__(self):
        super(ZobbyApplication, self).__init__()
        self.users = PersistentList()

    def addUser(self, username):
        """Connects a user to the app."""
        self.users.append(username)

    def removeUser(self, username):
        """disconnect a user from the app."""
        self.users.remove(username)


class Session(btree.BTreeContainer):
    """a Zobby Session."""
    implements(interfaces.ISession)

    def __init__(self):
        super(Session, self).__init__()
        self.chatMessages = PersistentList()

    def addChatMessage(self, message):
        self.chatMessages.append(message)
