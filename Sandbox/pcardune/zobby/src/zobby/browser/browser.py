from jsonserver.jsonrpc import MethodPublisher

from zobby.zobby import Session

class ZobbyHandler(MethodPublisher):
    """simple json-rpc view class with two methods"""

    def newSession(self, name):
        self.context[name] = Session()
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

    
