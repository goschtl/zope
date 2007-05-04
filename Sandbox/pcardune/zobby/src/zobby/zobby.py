from persistent import Persistent
from persistent.list import PersistentList
from zope.interface import implements
from zope.app.container import btree
from zope.schema.fieldproperty import FieldProperty

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

    title = FieldProperty(interfaces.ISession['title'])
    description = FieldProperty(interfaces.ISession['description'])

    def __init__(self, title=u"Zobby Session", description=u"Default Description"):
        super(Session, self).__init__()
        self.title = title
        self.description = description
        self.chatMessages = PersistentList()

    def addChatMessage(self, message):
        self.chatMessages.append(message)
