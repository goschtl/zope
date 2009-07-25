#!/usr/bin/python
import sys
import twisted.cred.portal
import twisted.conch.avatar
import twisted.conch.checkers
import twisted.conch.ssh.factory
import twisted.conch.ssh.userauth
import twisted.conch.ssh.connection
import twisted.conch.ssh.keys
import twisted.conch.ssh.session
import twisted.internet.reactor
import twisted.internet.protocol
import twisted.python.components
import twisted.python.log
import zope.interface

twisted.python.log.startLogging(sys.stderr)

"""Example of running another protocol over an SSH channel.
log in with username "user" and password "password".
"""

class ExampleAvatar(twisted.conch.avatar.ConchUser):

    def __init__(self, username):
        twisted.conch.avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update(
            {'session':twisted.conch.ssh.session.SSHSession}
            )

class ExampleRealm:
    zope.interface.implements(twisted.cred.portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        return interfaces[0], ExampleAvatar(avatarId), lambda: None

class EchoProtocol(twisted.internet.protocol.Protocol):
    """this is our example protocol that we will run over SSH
    """
    def dataReceived(self, data):
        if data == '\r':
            data = '\r\n'
        elif data == '\x03': #^C
            self.transport.loseConnection()
            return
        self.transport.write(data.upper())


user_pubkey = twisted.conch.ssh.keys.Key.fromFile('ukey.pub')

class InMemoryPublicKeyChecker(twisted.conch.checkers.SSHPublicKeyDatabase):

    def checkKey(self, credentials):
        return (credentials.username == 'user' and
                user_pubkey.blob() == credentials.blob)

class ExampleSession:

    def __init__(self, avatar):
        """
        We don't use it, but the adapter is passed the avatar as its first
        argument.
        """

    def getPty(self, term, windowSize, attrs):
        pass

    def execCommand(self, proto, cmd):
        raise Exception("no executing commands")

    def openShell(self, trans):
        ep = EchoProtocol()
        ep.makeConnection(trans)
        trans.makeConnection(twisted.conch.ssh.session.wrapProtocol(ep))

    def eofReceived(self):
        pass

    def closed(self):
        pass

twisted.python.components.registerAdapter(
    ExampleSession, ExampleAvatar, twisted.conch.ssh.session.ISession)

class ExampleFactory(twisted.conch.ssh.factory.SSHFactory):
    publicKeys = {
        'ssh-rsa': twisted.conch.ssh.keys.Key.fromFile('skey.pub')
    }
    privateKeys = {
        'ssh-rsa': twisted.conch.ssh.keys.Key.fromFile('skey')
    }
    services = {
        'ssh-userauth': twisted.conch.ssh.userauth.SSHUserAuthServer,
        'ssh-connection': twisted.conch.ssh.connection.SSHConnection
    }

portal = twisted.cred.portal.Portal(ExampleRealm())
portal.registerChecker(InMemoryPublicKeyChecker())
ExampleFactory.portal = portal

if __name__ == '__main__':
    twisted.internet.reactor.listenTCP(5022, ExampleFactory())
    twisted.internet.reactor.run()
