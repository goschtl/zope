from zif.jsonserver.jsonrpc import MethodPublisher

from zobby import zobby


## class ZobbyApplicationAddForm(form.AddForm):
##     """An add form for the zobby application."""

##     template = None
##     layout = None
##     contentName = None
##     label = u'Add Zobby Application'

##     fields = field.Fields()

##     def create(self, data):
##         return zobby.ZobbyApplication(**data)

##     def add(self, object):
##         self._name = object.title
##         self.context[object.title] = object

##     def nextURL(self):
##         return absoluteURL(self.context[self._name], self.request)

##     def __call__(self):
##         self.update()
##         if self._finishedAdd:
##             self.request.response.redirect(self.nextURL())
##             return ''
##         layout = zope.component.getMultiAdapter((self, self.request),
##                                                 ILayoutTemplate)
##         return layout(self)


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

    
