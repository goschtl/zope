from zif.jsonserver.jsonrpc import MethodPublisher
from zope.traversing.browser import absoluteURL

from z3c.formui import layout
from z3c.form import form, field, button

from zobby import zobby
from zobby import interfaces


class ZobbyApplicationDisplayForm(object):
    pass


class SessionAddForm(layout.AddFormLayoutSupport, form.AddForm):
    """An add form for the zobby application."""

    layout = None
    contentName = None
    label = u'Add Zobby Session'

    fields = field.Fields(interfaces.ISession).omit('chatMessages')

    def create(self, data):
        return zobby.Session(**data)

    def add(self, object):
        self._name = object.title
        self.context[object.title] = object
        return object

    def nextURL(self):
        return absoluteURL(self.context[self._name], self.request)


class ZobbyHandler(MethodPublisher):
    """simple json-rpc view class with two methods"""

    def newSession(self, name):
        self.context[name] = zobby.Session()
        return "Created a new session named %s"% name

    def getSessions(self):
        return list(self.context.keys())

    def testConnection(self):
        return "You are successfully connected to %s" % self.context.__name__

    def connectUser(self, username):
        self.context.addUser(username)
        return "You have been connected to the server with username %s" % username

    def disconnectUser(self, username):
        self.context.removeUser(username)
        return "You have been disconnected from the server."

class SessionHandler(MethodPublisher):
    """simple json-rpc view class for handling sessions."""

    def testConnection(self):
        return "You are successfully connected to session %s" % self.context.__name__

    def sendChat(self, message, index):
        self.context.addChatMessage(message)
        return list(self.context.chatMessages[index:])

    def getChatMessages(self, index):
        return list(self.context.chatMessages[index:])

    
